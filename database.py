"""
数据库操作模块
"""
import sqlite3
import os
from config import DATABASE_PATH

class Database:
    def __init__(self):
        """初始化数据库连接"""
        # 确保data目录存在
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.conn.row_factory = sqlite3.Row  # 返回字典格式
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        """创建数据表"""
        # 费用记录表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expense_type TEXT NOT NULL,
                project TEXT DEFAULT '默认项目',
                name TEXT NOT NULL,
                quantity REAL,
                unit_price REAL,
                total_amount REAL NOT NULL,
                expense_date DATE DEFAULT (date('now')),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 公式配置表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS formulas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                formula_name TEXT NOT NULL UNIQUE,
                display_name TEXT NOT NULL,
                expression TEXT NOT NULL,
                parameters TEXT NOT NULL,
                description TEXT,
                is_custom INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 插入预定义公式
        self._initialize_predefined_formulas()
        
        self.conn.commit()
    
    def _initialize_predefined_formulas(self):
        """初始化预定义公式"""
        from config import PREDEFINED_FORMULAS
        
        for key, formula in PREDEFINED_FORMULAS.items():
            # 检查是否已存在
            self.cursor.execute(
                "SELECT id FROM formulas WHERE formula_name = ?", 
                (key,)
            )
            if not self.cursor.fetchone():
                self.cursor.execute('''
                    INSERT INTO formulas 
                    (formula_name, display_name, expression, parameters, description, is_custom)
                    VALUES (?, ?, ?, ?, ?, 0)
                ''', (
                    key,
                    formula['name'],
                    formula['expression'],
                    ','.join(formula['params']),
                    formula['description']
                ))
        
        self.conn.commit()
    
    def add_expense(self, expense_data):
        """添加费用记录"""
        query = '''
            INSERT INTO expenses 
            (expense_type, project, name, quantity, unit_price, total_amount, expense_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.cursor.execute(query, (
            expense_data['expense_type'],
            expense_data.get('project', '默认项目'),
            expense_data['name'],
            expense_data.get('quantity'),
            expense_data.get('unit_price'),
            expense_data['total_amount'],
            expense_data.get('expense_date'),
            expense_data.get('notes')
        ))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_expenses(self):
        """获取所有费用记录"""
        self.cursor.execute('''
            SELECT * FROM expenses 
            ORDER BY expense_date DESC, created_at DESC
        ''')
        return self.cursor.fetchall()
    
    def get_expenses_by_type(self, expense_type):
        """按类型获取费用记录"""
        self.cursor.execute('''
            SELECT * FROM expenses 
            WHERE expense_type = ?
            ORDER BY expense_date DESC
        ''', (expense_type,))
        return self.cursor.fetchall()
    
    def get_expenses_by_project(self, project):
        """按项目获取费用记录"""
        self.cursor.execute('''
            SELECT * FROM expenses 
            WHERE project = ?
            ORDER BY expense_date DESC
        ''', (project,))
        return self.cursor.fetchall()
    
    def get_all_projects(self):
        """获取所有项目"""
        self.cursor.execute('''
            SELECT DISTINCT project 
            FROM expenses 
            WHERE project IS NOT NULL AND project != ''
            ORDER BY project
        ''')
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_expense_statistics_by_project(self):
        """按项目获取费用统计"""
        # 按项目统计
        self.cursor.execute('''
            SELECT 
                project,
                COUNT(*) as count,
                SUM(total_amount) as total_amount,
                AVG(total_amount) as avg_amount
            FROM expenses
            GROUP BY project
            ORDER BY total_amount DESC
        ''')
        project_stats = self.cursor.fetchall()
        
        return [dict(row) for row in project_stats]
    
    def get_expense_statistics(self):
        """获取费用统计"""
        # 按类型统计
        self.cursor.execute('''
            SELECT 
                expense_type,
                COUNT(*) as count,
                SUM(total_amount) as total_amount
            FROM expenses
            GROUP BY expense_type
            ORDER BY total_amount DESC
        ''')
        type_stats = self.cursor.fetchall()
        
        # 按项目统计
        project_stats = self.get_expense_statistics_by_project()
        
        # 总体统计
        self.cursor.execute('''
            SELECT 
                COUNT(*) as total_count,
                SUM(total_amount) as grand_total,
                AVG(total_amount) as avg_amount,
                MIN(expense_date) as earliest_date,
                MAX(expense_date) as latest_date
            FROM expenses
        ''')
        overall_stats = self.cursor.fetchone()
        
        return {
            'by_type': [dict(row) for row in type_stats],
            'by_project': project_stats,
            'overall': dict(overall_stats) if overall_stats else {}
        }
    
    def add_custom_formula(self, formula_data):
        """添加自定义公式"""
        query = '''
            INSERT INTO formulas 
            (formula_name, display_name, expression, parameters, description, is_custom)
            VALUES (?, ?, ?, ?, ?, 1)
        '''
        self.cursor.execute(query, (
            formula_data['formula_name'],
            formula_data['display_name'],
            formula_data['expression'],
            formula_data['parameters'],
            formula_data.get('description', '')
        ))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_formulas(self):
        """获取所有公式"""
        self.cursor.execute('''
            SELECT * FROM formulas 
            ORDER BY is_custom, formula_name
        ''')
        return self.cursor.fetchall()
    
    def get_formula_by_name(self, formula_name):
        """根据名称获取公式"""
        self.cursor.execute(
            "SELECT * FROM formulas WHERE formula_name = ?", 
            (formula_name,)
        )
        result = self.cursor.fetchone()
        return dict(result) if result else None
    
    def delete_expense(self, expense_id):
        """删除费用记录"""
        self.cursor.execute(
            "DELETE FROM expenses WHERE id = ?", 
            (expense_id,)
        )
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# 单例数据库实例
db_instance = None

def get_db():
    """获取数据库实例"""
    global db_instance
    if db_instance is None:
        db_instance = Database()
    return db_instance