"""
费用管理模块
"""
import datetime
from config import EXPENSE_TYPES
from database import get_db

class ExpenseManager:
    def __init__(self):
        self.db = get_db()
    
    def calculate_expense(self, formula_name, params):
        """计算费用"""
        formula = self.db.get_formula_by_name(formula_name)
        if not formula:
            raise ValueError(f"找不到公式: {formula_name}")
        
        # 解析参数
        param_list = formula['parameters'].split(',')
        
        # 检查参数是否完整
        for param in param_list:
            if param not in params:
                raise ValueError(f"缺少参数: {param}")
        
        # 安全地执行表达式
        try:
            # 使用安全的数学计算
            result = eval(formula['expression'], {"__builtins__": {}}, params)
            return float(result)
        except Exception as e:
            raise ValueError(f"公式计算错误: {str(e)}")
    
    def add_expense_record(self):
        """添加费用记录（交互式）"""
        print("\n=== 添加费用记录 ===")
        
        # 选择费用类型
        print("\n请选择费用类型:")
        type_keys = list(EXPENSE_TYPES.keys())
        for i, key in enumerate(type_keys, 1):
            print(f"{i}. {EXPENSE_TYPES[key]}")
        
        try:
            type_choice = int(input(f"请选择 [1-{len(type_keys)}]: "))
            if type_choice < 1 or type_choice > len(type_keys):
                raise ValueError("无效选择")
            expense_type = type_keys[type_choice - 1]
        except ValueError:
            print("无效输入，使用默认类型 'other'")
            expense_type = "other"
        
        # 输入费用名称
        name = input("费用名称: ").strip()
        if not name:
            print("费用名称不能为空")
            return None
        
        # 选择或输入公式
        formulas = self.db.get_all_formulas()
        print("\n可用计算公式:")
        for i, formula in enumerate(formulas, 1):
            formula_dict = dict(formula)
            custom_tag = "[自定义]" if formula_dict['is_custom'] else ""
            print(f"{i}. {formula_dict['display_name']} {custom_tag}")
            print(f"   公式: {formula_dict['expression']}")
            print(f"   参数: {formula_dict['parameters']}")
            if formula_dict['description']:
                print(f"   说明: {formula_dict['description']}")
            print()
        
        try:
            formula_choice = int(input(f"选择公式 [1-{len(formulas)}], 或输入0使用手动输入金额: "))
            if formula_choice == 0:
                # 手动输入金额
                try:
                    total_amount = float(input("请输入总金额: "))
                except ValueError:
                    print("无效金额")
                    return None
            else:
                formula = dict(formulas[formula_choice - 1])
                param_list = formula['parameters'].split(',')
                params = {}
                
                # 输入参数值
                print(f"\n请输入公式参数:")
                for param in param_list:
                    try:
                        value = float(input(f"{param}: "))
                        params[param] = value
                    except ValueError:
                        print(f"参数 {param} 无效，必须为数字")
                        return None
                
                # 计算总金额
                total_amount = self.calculate_expense(formula['formula_name'], params)
                print(f"计算出的总金额: {total_amount}")
        
        except (ValueError, IndexError):
            print("无效选择")
            return None
        
        # 输入其他信息
        quantity = input("数量 (可选，按Enter跳过): ").strip()
        unit_price = input("单价 (可选，按Enter跳过): ").strip()
        expense_date = input("费用日期 (YYYY-MM-DD, 可选，按Enter使用今天): ").strip()
        notes = input("备注 (可选): ").strip()
        
        # 处理输入
        expense_data = {
            'expense_type': expense_type,
            'name': name,
            'total_amount': total_amount,
            'notes': notes
        }
        
        if quantity:
            try:
                expense_data['quantity'] = float(quantity)
            except ValueError:
                print("数量格式错误，已忽略")
        
        if unit_price:
            try:
                expense_data['unit_price'] = float(unit_price)
            except ValueError:
                print("单价格式错误，已忽略")
        
        if expense_date:
            try:
                # 验证日期格式
                datetime.datetime.strptime(expense_date, '%Y-%m-%d')
                expense_data['expense_date'] = expense_date
            except ValueError:
                print("日期格式错误，使用今天日期")
        
        # 保存到数据库
        try:
            expense_id = self.db.add_expense(expense_data)
            print(f"\n✅ 费用记录添加成功! ID: {expense_id}")
            return expense_id
        except Exception as e:
            print(f"❌ 保存失败: {str(e)}")
            return None
    
    def view_all_expenses(self):
        """查看所有费用记录"""
        expenses = self.db.get_all_expenses()
        
        if not expenses:
            print("\n暂无费用记录")
            return
        
        print(f"\n=== 所有费用记录 (共{len(expenses)}条) ===")
        print("-" * 80)
        print(f"{'ID':<4} {'日期':<12} {'类型':<8} {'名称':<20} {'数量':<8} {'单价':<8} {'总金额':<10} {'备注'}")
        print("-" * 80)
        
        total = 0
        for expense in expenses:
            exp_dict = dict(expense)
            expense_type = EXPENSE_TYPES.get(exp_dict['expense_type'], exp_dict['expense_type'])
            
            print(f"{exp_dict['id']:<4} "
                  f"{exp_dict['expense_date']:<12} "
                  f"{expense_type:<8} "
                  f"{exp_dict['name']:<20} "
                  f"{exp_dict['quantity'] or '-':<8} "
                  f"{exp_dict['unit_price'] or '-':<8} "
                  f"{exp_dict['total_amount']:<10.2f} "
                  f"{exp_dict['notes'] or ''}")
            
            total += exp_dict['total_amount']
        
        print("-" * 80)
        print(f"{'总计:':<68} {total:.2f}")
    
    def view_expenses_by_type(self):
        """按类型查看费用记录"""
        print("\n=== 按类型查看费用 ===")
        
        type_keys = list(EXPENSE_TYPES.keys())
        for i, key in enumerate(type_keys, 1):
            print(f"{i}. {EXPENSE_TYPES[key]}")
        
        try:
            type_choice = int(input(f"请选择类型 [1-{len(type_keys)}]: "))
            if type_choice < 1 or type_choice > len(type_keys):
                raise ValueError("无效选择")
            expense_type = type_keys[type_choice - 1]
        except ValueError:
            print("无效输入")
            return
        
        expenses = self.db.get_expenses_by_type(expense_type)
        
        if not expenses:
            print(f"\n暂无 {EXPENSE_TYPES[expense_type]} 记录")
            return
        
        type_name = EXPENSE_TYPES[expense_type]
        print(f"\n=== {type_name} 费用记录 (共{len(expenses)}条) ===")
        print("-" * 70)
        print(f"{'ID':<4} {'日期':<12} {'名称':<20} {'数量':<8} {'单价':<8} {'总金额':<10} {'备注'}")
        print("-" * 70)
        
        type_total = 0
        for expense in expenses:
            exp_dict = dict(expense)
            print(f"{exp_dict['id']:<4} "
                  f"{exp_dict['expense_date']:<12} "
                  f"{exp_dict['name']:<20} "
                  f"{exp_dict['quantity'] or '-':<8} "
                  f"{exp_dict['unit_price'] or '-':<8} "
                  f"{exp_dict['total_amount']:<10.2f} "
                  f"{exp_dict['notes'] or ''}")
            
            type_total += exp_dict['total_amount']
        
        print("-" * 70)
        print(f"{'类型总计:':<52} {type_total:.2f}")
    
    def show_statistics(self):
        """显示统计信息"""
        stats = self.db.get_expense_statistics()
        
        print("\n=== 费用统计 ===")
        
        if not stats['overall']:
            print("暂无统计数据")
            return
        
        overall = stats['overall']
        print(f"\n📊 总体统计:")
        print(f"  总记录数: {overall.get('total_count', 0)}")
        print(f"  总费用: {overall.get('grand_total', 0):.2f}")
        print(f"  平均费用: {overall.get('avg_amount', 0):.2f}")
        if overall.get('earliest_date'):
            print(f"  最早记录: {overall['earliest_date']}")
        if overall.get('latest_date'):
            print(f"  最新记录: {overall['latest_date']}")
        
        if stats['by_type']:
            print(f"\n📈 按类型统计:")
            print("-" * 50)
            print(f"{'类型':<12} {'记录数':<8} {'总金额':<12} {'占比'}")
            print("-" * 50)
            
            grand_total = overall.get('grand_total', 1)  # 避免除零
            for type_stat in stats['by_type']:
                expense_type = EXPENSE_TYPES.get(type_stat['expense_type'], type_stat['expense_type'])
                percentage = (type_stat['total_amount'] / grand_total * 100) if grand_total > 0 else 0
                print(f"{expense_type:<12} "
                      f"{type_stat['count']:<8} "
                      f"{type_stat['total_amount']:<12.2f} "
                      f"{percentage:.1f}%")
    
    def add_custom_formula_interactive(self):
        """交互式添加自定义公式"""
        print("\n=== 添加自定义公式 ===")
        
        formula_name = input("公式代号 (英文，用于内部引用): ").strip()
        if not formula_name:
            print("公式代号不能为空")
            return
        
        # 检查是否已存在
        existing = self.db.get_formula_by_name(formula_name)
        if existing:
            print(f"公式代号 '{formula_name}' 已存在")
            return
        
        display_name = input("公式显示名称: ").strip()
        if not display_name:
            print("显示名称不能为空")
            return
        
        expression = input("计算公式表达式 (例如: a * b + c): ").strip()
        if not expression:
            print("表达式不能为空")
            return
        
        parameters = input("参数列表 (用逗号分隔，例如: a,b,c): ").strip()
        if not parameters:
            print("参数列表不能为空")
            return
        
        description = input("公式描述 (可选): ").strip()
        
        formula_data = {
            'formula_name': formula_name,
            'display_name': display_name,
            'expression': expression,
            'parameters': parameters,
            'description': description
        }
        
        try:
            formula_id = self.db.add_custom_formula(formula_data)
            print(f"\n✅ 自定义公式添加成功! ID: {formula_id}")
        except Exception as e:
            print(f"❌ 添加失败: {str(e)}")
    
    def delete_expense_record(self):
        """删除费用记录"""
        self.view_all_expenses()
        
        try:
            expense_id = int(input("\n请输入要删除的费用记录ID (输入0取消): "))
            if expense_id == 0:
                return
            
            confirm = input(f"确认删除记录 {expense_id}? (输入 'yes' 确认): ").lower()
            if confirm == 'yes':
                success = self.db.delete_expense(expense_id)
                if success:
                    print("✅ 记录删除成功")
                else:
                    print("❌ 找不到该记录")
            else:
                print("操作已取消")
        except ValueError:
            print("无效的ID")