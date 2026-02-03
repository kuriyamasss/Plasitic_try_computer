"""
导出管理模块
"""
import os
import pandas as pd
from datetime import datetime
from config import EXPENSE_TYPES, EXPORT_DIR, EXPORT_FORMATS
from database import get_db

class ExportManager:
    def __init__(self):
        self.db = get_db()
        # 确保导出目录存在
        os.makedirs(EXPORT_DIR, exist_ok=True)
    
    def get_export_data(self, expense_type=None, start_date=None, end_date=None):
        """获取要导出的数据"""
        if expense_type:
            expenses = self.db.get_expenses_by_type(expense_type)
        else:
            expenses = self.db.get_all_expenses()
        
        # 转换为DataFrame
        data = []
        for expense in expenses:
            exp_dict = dict(expense)
            expense_type_name = EXPENSE_TYPES.get(
                exp_dict['expense_type'], 
                exp_dict['expense_type']
            )
            
            data.append({
                'ID': exp_dict['id'],
                '日期': exp_dict['expense_date'],
                '类型': expense_type_name,
                '名称': exp_dict['name'],
                '数量': exp_dict['quantity'],
                '单价': exp_dict['unit_price'],
                '总金额': exp_dict['total_amount'],
                '备注': exp_dict['notes'],
                '创建时间': exp_dict['created_at']
            })
        
        # 创建DataFrame
        df = pd.DataFrame(data)
        
        # 如果有日期筛选条件
        if start_date or end_date:
            if '日期' in df.columns and not df.empty:
                df['日期'] = pd.to_datetime(df['日期'])
                
                if start_date:
                    start_dt = pd.to_datetime(start_date)
                    df = df[df['日期'] >= start_dt]
                
                if end_date:
                    end_dt = pd.to_datetime(end_date)
                    df = df[df['日期'] <= end_dt]
        
        return df
    
    def get_statistics_summary(self, df):
        """获取统计摘要"""
        if df.empty:
            return {}
        
        # 确保日期列是datetime类型
        if '日期' in df.columns and not df.empty:
            try:
                # 尝试将日期列转换为datetime
                df['日期'] = pd.to_datetime(df['日期'])
            except:
                # 如果转换失败，使用当前时间
                pass
        
        summary = {
            '记录总数': len(df),
            '总金额': df['总金额'].sum(),
            '平均金额': df['总金额'].mean(),
            '最大金额': df['总金额'].max(),
            '最小金额': df['总金额'].min(),
        }
        
        # 添加时间范围（如果日期列可用）
        if '日期' in df.columns and not df.empty and pd.api.types.is_datetime64_any_dtype(df['日期']):
            try:
                time_range = f"{df['日期'].min().strftime('%Y-%m-%d')} 到 {df['日期'].max().strftime('%Y-%m-%d')}"
                summary['时间范围'] = time_range
            except:
                summary['时间范围'] = "日期格式错误"
        
        # 按类型统计
        if '类型' in df.columns:
            type_stats = df.groupby('类型').agg({
                'ID': 'count',
                '总金额': 'sum'
            }).rename(columns={'ID': '记录数'})
            summary['按类型统计'] = type_stats
        
        return summary
    
    def export_to_excel(self, df, filename=None):
        """导出为Excel文件"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"expenses_export_{timestamp}.xlsx"
        
        filepath = os.path.join(EXPORT_DIR, filename)
        
        try:
            # 创建Excel写入器
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # 写入主数据
                df.to_excel(writer, sheet_name='费用记录', index=False)
                
                # 获取统计摘要
                summary = self.get_statistics_summary(df)
                
                # 创建统计工作表
                summary_data = []
                for key, value in summary.items():
                    if key != '按类型统计':
                        if isinstance(value, float):
                            value = f"{value:.2f}"
                        summary_data.append([key, value])
                
                summary_df = pd.DataFrame(summary_data, columns=['项目', '值'])
                summary_df.to_excel(writer, sheet_name='统计摘要', index=False)
                
                # 如果有类型统计，写入单独的工作表
                if '按类型统计' in summary and not summary['按类型统计'].empty:
                    type_stats_df = summary['按类型统计'].reset_index()
                    type_stats_df['总金额'] = type_stats_df['总金额'].apply(lambda x: f"{x:.2f}")
                    type_stats_df.to_excel(writer, sheet_name='类型统计', index=False)
            
            return filepath, True
        except Exception as e:
            print(f"导出Excel失败: {str(e)}")
            return None, False
    
    def export_to_csv(self, df, filename=None):
        """导出为CSV文件"""
        try:
            # 始终生成时间戳，用于统计文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if filename is None:
                filename = f"expenses_export_{timestamp}.csv"
            
            filepath = os.path.join(EXPORT_DIR, filename)
            
            # 导出主数据
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            
            # 创建统计摘要文件
            stats_filename = f"expenses_stats_{timestamp}.txt"
            stats_filepath = os.path.join(EXPORT_DIR, stats_filename)
            self._create_stats_file(df, stats_filepath, timestamp)
            
            return filepath, True
        except Exception as e:
            print(f"导出CSV失败: {str(e)}")
            return None, False
    
    def _create_stats_file(self, df, filepath, timestamp=None):
        """创建统计摘要文本文件"""
        summary = self.get_statistics_summary(df)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("费用统计摘要\n")
            f.write("=" * 50 + "\n\n")
            
            # 写入基本统计
            f.write("基本统计:\n")
            f.write("-" * 30 + "\n")
            for key, value in summary.items():
                if key != '按类型统计':
                    f.write(f"{key}: {value}\n")
            
            # 写入类型统计
            if '按类型统计' in summary and not summary['按类型统计'].empty:
                f.write("\n按类型统计:\n")
                f.write("-" * 30 + "\n")
                type_stats = summary['按类型统计']
                for index, row in type_stats.iterrows():
                    f.write(f"{index}: {row['记录数']}条记录, 总金额: {row['总金额']:.2f}\n")
            
            export_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if timestamp:
                f.write(f"\n导出时间: {export_time}\n")
                f.write(f"导出批次: {timestamp}\n")
            else:
                f.write(f"\n导出时间: {export_time}\n")
    
    def interactive_export(self):
        """交互式导出"""
        print("\n=== 数据导出 ===")
        
        # 选择导出格式
        print("\n请选择导出格式:")
        for i, fmt in enumerate(EXPORT_FORMATS, 1):
            print(f"{i}. {fmt.upper()}")
        
        try:
            format_choice = int(input(f"请选择格式 [1-{len(EXPORT_FORMATS)}]: "))
            if format_choice < 1 or format_choice > len(EXPORT_FORMATS):
                raise ValueError("无效选择")
            export_format = EXPORT_FORMATS[format_choice - 1]
        except ValueError:
            print("无效输入，使用默认格式: excel")
            export_format = "excel"
        
        # 选择导出范围
        print("\n导出范围:")
        print("1. 全部费用记录")
        print("2. 按类型导出")
        print("3. 按日期范围导出")
        
        try:
            range_choice = int(input("请选择范围 [1-3]: "))
        except ValueError:
            print("无效输入，导出全部记录")
            range_choice = 1
        
        expense_type = None
        start_date = None
        end_date = None
        
        if range_choice == 2:
            # 按类型导出
            from config import EXPENSE_TYPES
            type_keys = list(EXPENSE_TYPES.keys())
            print("\n请选择费用类型:")
            for i, key in enumerate(type_keys, 1):
                print(f"{i}. {EXPENSE_TYPES[key]}")
            
            try:
                type_choice = int(input(f"请选择类型 [1-{len(type_keys)}]: "))
                if type_choice < 1 or type_choice > len(type_keys):
                    raise ValueError("无效选择")
                expense_type = type_keys[type_choice - 1]
            except ValueError:
                print("无效输入，导出全部记录")
        
        elif range_choice == 3:
            # 按日期范围导出
            try:
                start_date = input("开始日期 (YYYY-MM-DD，可选): ").strip()
                if start_date:
                    # 验证日期格式
                    datetime.strptime(start_date, '%Y-%m-%d')
                
                end_date = input("结束日期 (YYYY-MM-DD，可选): ").strip()
                if end_date:
                    # 验证日期格式
                    datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                print("日期格式错误，使用默认范围")
                start_date = None
                end_date = None
        
        # 自定义文件名
        custom_name = input("自定义文件名 (可选，按Enter使用默认): ").strip()
        
        # 获取数据
        print("\n正在获取数据...")
        df = self.get_export_data(expense_type, start_date, end_date)
        
        if df.empty:
            print("没有找到符合条件的数据")
            return
        
        print(f"找到 {len(df)} 条记录")
        
        # 执行导出
        filename = custom_name if custom_name else None
        
        if export_format == 'excel':
            filepath, success = self.export_to_excel(df, filename)
            if success:
                print(f"\n✅ Excel文件导出成功!")
                print(f"文件位置: {os.path.abspath(filepath)}")
            else:
                print("❌ 导出失败")
        
        elif export_format == 'csv':
            filepath, success = self.export_to_csv(df, filename)
            if success:
                print(f"\n✅ CSV文件导出成功!")
                print(f"文件位置: {os.path.abspath(filepath)}")
                # 同时生成了统计文件
                stats_filepath = filepath.replace('.csv', '_stats.txt')
                if os.path.exists(stats_filepath):
                    print(f"统计文件: {os.path.abspath(stats_filepath)}")
            else:
                print("❌ 导出失败")
        
        else:
            print(f"不支持的导出格式: {export_format}")
    
    def list_exports(self):
        """列出所有导出文件"""
        if not os.path.exists(EXPORT_DIR):
            print(f"导出目录 {EXPORT_DIR} 不存在")
            return
        
        files = os.listdir(EXPORT_DIR)
        if not files:
            print("暂无导出文件")
            return
        
        print(f"\n=== 导出文件列表 ({EXPORT_DIR}) ===")
        
        # 按扩展名分类
        excel_files = [f for f in files if f.endswith(('.xlsx', '.xls'))]
        csv_files = [f for f in files if f.endswith('.csv')]
        txt_files = [f for f in files if f.endswith('.txt')]
        
        if excel_files:
            print("\nExcel文件:")
            for file in sorted(excel_files):
                filepath = os.path.join(EXPORT_DIR, file)
                size = os.path.getsize(filepath)
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                print(f"  {file} ({size:,} bytes, {mtime.strftime('%Y-%m-%d %H:%M')})")
        
        if csv_files:
            print("\nCSV文件:")
            for file in sorted(csv_files):
                filepath = os.path.join(EXPORT_DIR, file)
                size = os.path.getsize(filepath)
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                print(f"  {file} ({size:,} bytes, {mtime.strftime('%Y-%m-%d %H:%M')})")
        
        if txt_files:
            print("\n文本文件:")
            for file in sorted(txt_files):
                filepath = os.path.join(EXPORT_DIR, file)
                size = os.path.getsize(filepath)
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                print(f"  {file} ({size:,} bytes, {mtime.strftime('%Y-%m-%d %H:%M')})")