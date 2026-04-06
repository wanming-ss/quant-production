#!/usr/bin/env python3
"""
DolphinDB to Qlib Data Bridge
将 DolphinDB 中的因子数据导出为 Qlib 格式
"""
import dolphindb as ddb
import pandas as pd
import numpy as np
from pathlib import Path

class DolphinDBQlibBridge:
    """DolphinDB 与 Qlib 数据桥接"""
    
    def __init__(self, host="localhost", port=8848, user="admin", password="123456"):
        self.session = ddb.session()
        self.session.connect(host, port, user, password)
        print("✅ Connected to DolphinDB")
    
    def load_factor_data(self, db_name, table_name, factor_cols=None):
        """
        从 DolphinDB 加载因子数据
        
        Parameters:
        -----------
        db_name : str
            数据库名称，如 "dfs://tushare"
        table_name : str
            表名称，如 "daily"
        factor_cols : list
            需要的因子列名列表
        
        Returns:
        --------
        pd.DataFrame
            Qlib 格式的因子数据
        """
        print(f"📊 Loading data from {db_name}/{table_name}...")
        
        # 构建查询
        if factor_cols:
            cols_str = ", ".join(factor_cols)
            query = f"select symbol, date, {cols_str} from loadTable('{db_name}', '{table_name}')"
        else:
            query = f"select * from loadTable('{db_name}', '{table_name}')"
        
        # 执行查询
        result = self.session.run(query)
        df = pd.DataFrame(result)
        
        print(f"✅ Loaded {len(df):,} records")
        return df
    
    def convert_to_qlib_format(self, df, symbol_col='symbol', date_col='date'):
        """
        转换为 Qlib 格式
        
        Qlib 要求列名: ['datetime', 'instrument', 'feature1', 'feature2', ...]
        """
        df = df.copy()
        
        # 重命名列为 Qlib 格式
        df.rename(columns={
            symbol_col: 'instrument',
            date_col: 'datetime'
        }, inplace=True)
        
        # 确保 datetime 格式正确
        df['datetime'] = pd.to_datetime(df['datetime'])
        
        # Qlib 通常使用交易日历，这里简化为日期
        df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d')
        
        # 股票代码格式调整 (移除交易所后缀)
        df['instrument'] = df['instrument'].str.replace('.SH', '').str.replace('.SZ', '').str.replace('.BJ', '')
        
        return df
    
    def save_to_qlib_csv(self, df, output_path):
        """保存为 Qlib 可读取的 CSV 格式"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"💾 Saved to {output_path}")
    
    def export_pv_divergence_factor(self, output_dir="E:/Quant_Production/Vault/qlib_data"):
        """
        导出量价背离因子到 Qlib
        """
        print("="*70)
        print("Exporting Price-Volume Divergence Factor to Qlib")
        print("="*70)
        
        # 1. 加载日线数据
        daily_df = self.load_factor_data(
            "dfs://tushare", 
            "daily",
            factor_cols=['close', 'volume', 'open', 'high', 'low']
        )
        
        # 2. 转换为 Qlib 格式
        qlib_df = self.convert_to_qlib_format(daily_df)
        
        # 3. 保存
        self.save_to_qlib_csv(qlib_df, f"{output_dir}/daily_features.csv")
        
        # 4. 如果有计算好的因子数据，也导出
        try:
            factor_df = self.load_factor_data(
                "dfs://tushare_factors",
                "pv_divergence",
                factor_cols=['divergence_zscore', 'pv_corr', 'rel_volume']
            )
            factor_qlib_df = self.convert_to_qlib_format(factor_df)
            self.save_to_qlib_csv(factor_qlib_df, f"{output_dir}/pv_divergence_factor.csv")
        except:
            print("⚠️ Factor table not found, skipping factor export")
        
        print("="*70)
        print("Export completed!")
        print("="*70)
        
        return qlib_df

# 使用示例
if __name__ == "__main__":
    # 创建桥接实例
    bridge = DolphinDBQlibBridge()
    
    # 导出数据
    df = bridge.export_pv_divergence_factor()
    
    print(f"\n📊 Data shape: {df.shape}")
    print(f"📅 Date range: {df['datetime'].min()} to {df['datetime'].max()}")
    print(f"🔢 Instruments: {df['instrument'].nunique()}")
    print(f"\n📁 Output: E:/Quant_Production/Vault/qlib_data/")
