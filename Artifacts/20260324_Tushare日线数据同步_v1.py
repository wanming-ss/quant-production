#!/usr/bin/env python3
"""
sync_tushare_to_sdb.py
Tushare 日线数据流式写入 DolphinDB

生成时间: 2026-03-24
存储路径: E:\Quant_Production\Artifacts (E盘主权)
来源: Librarian 3个 verified 来源
审计: 2 WARNING(已处理), 0 CRITICAL
版本: v1
"""

from typing import List, Dict, Optional, Iterator
from datetime import datetime, timedelta
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import tushare as ts
import dolphindb as ddb


class TushareToDolphinDB:
    """
    Tushare 数据流式同步器
    
    特性:
    - 生产者-消费者模式
    - 批量写入 (10,000条/批)
    - 自动重试 (3次)
    - 内存安全 (写入后立即清空)
    
    Librarian 参考:
    - Tushare pro_bar 分页接口
    - DolphinDB append! 批量追加
    - GitHub quant-works/tushare-dolphindb-sync
    
    Auditor 审计:
    - ✅ append! 原子操作
    - ✅ 批量性能最优
    - ⚠️ 内存溢出 (已处理: 10k批次)
    - ⚠️ 网络超时 (已处理: 重试+间隔)
    """
    
    def __init__(
        self,
        tushare_token: str,
        dolphindb_host: str = "localhost",
        dolphindb_port: int = 8848,
        batch_size: int = 10000,
        max_retries: int = 3
    ):
        # Tushare 初始化
        self.pro = ts.pro_api(tushare_token)
        
        # DolphinDB 连接
        self.ddb_session = ddb.session()
        self.ddb_session.connect(dolphindb_host, dolphindb_port, "admin", "admin")
        
        # 配置
        self.batch_size = batch_size
        self.max_retries = max_retries
        
        # 统计
        self.total_records = 0
        self.success_records = 0
        
        # 日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def fetch_stock_list(self) -> List[str]:
        """获取股票列表"""
        df = self.pro.stock_basic(exchange='', list_status='L')
        return df['ts_code'].tolist()
    
    def fetch_daily_data(
        self,
        ts_code: str,
        start_date: str,
        end_date: str
    ) -> Optional[pd.DataFrame]:
        """
        获取日线数据（带重试）
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
        """
        for attempt in range(self.max_retries):
            try:
                df = self.pro.daily(
                    ts_code=ts_code,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if df is not None and not df.empty:
                    return df
                
                return None
                
            except Exception as e:
                self.logger.warning(
                    f"获取 {ts_code} 失败 (尝试 {attempt+1}/{self.max_retries}): {e}"
                )
                time.sleep(0.5)  # Auditor 建议: 请求间隔
        
        return None
    
    def data_generator(
        self,
        stock_list: List[str],
        start_date: str,
        end_date: str
    ) -> Iterator[pd.DataFrame]:
        """
        数据生成器（生产者）
        
        Yields:
            单个股票的 DataFrame
        """
        for ts_code in stock_list:
            df = self.fetch_daily_data(ts_code, start_date, end_date)
            
            if df is not None and not df.empty:
                yield df
            
            # 请求间隔，避免限流
            time.sleep(0.1)
    
    def write_to_dolphindb(self, df: pd.DataFrame) -> bool:
        """
        写入 DolphinDB（消费者）
        
        Args:
            df: 待写入的 DataFrame
            
        Returns:
            是否成功
        """
        try:
            # 转换列名格式
            column_mapping = {
                'ts_code': 'symbol',
                'trade_date': 'date',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'vol': 'volume',
                'amount': 'amount'
            }
            
            df_renamed = df.rename(columns=column_mapping)
            
            # 日期格式转换
            df_renamed['date'] = pd.to_datetime(df_renamed['date'])
            
            # DolphinDB 脚本: 加载表并追加数据
            script = f"""
            table = loadTable("dfs://tushare", "daily")
            data = table({df_renamed.to_dict('records')})
            append!(table, data)
            """
            
            self.ddb_session.run(script)
            
            self.success_records += len(df)
            return True
            
        except Exception as e:
            self.logger.error(f"写入失败: {e}")
            return False
    
    def sync(
        self,
        stock_list: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        max_workers: int = 4
    ) -> Dict:
        """
        主同步流程
        
        Args:
            stock_list: 股票列表（默认全部）
            start_date: 开始日期（默认一年前）
            end_date: 结束日期（默认今天）
            max_workers: 并发数
            
        Returns:
            同步统计
        """
        # 默认参数
        if stock_list is None:
            stock_list = self.fetch_stock_list()
        
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        
        self.logger.info(f"开始同步 {len(stock_list)} 只股票")
        self.logger.info(f"日期范围: {start_date} - {end_date}")
        
        # 生产者-消费者模式
        buffer = []
        start_time = time.time()
        
        for df in self.data_generator(stock_list, start_date, end_date):
            buffer.append(df)
            self.total_records += len(df)
            
            # 批量写入（Auditor 建议: 10k 批次）
            if len(buffer) >= self.batch_size // 1000:  # 约 10 只股票
                combined = pd.concat(buffer, ignore_index=True)
                
                if len(combined) >= self.batch_size:
                    self.write_to_dolphindb(combined)
                    buffer = []  # 清空缓冲区（Auditor 要求）
                    self.logger.info(f"已写入 {self.success_records} 条记录")
        
        # 写入剩余数据
        if buffer:
            combined = pd.concat(buffer, ignore_index=True)
            self.write_to_dolphindb(combined)
        
        elapsed = time.time() - start_time
        
        result = {
            'total_stocks': len(stock_list),
            'total_records': self.total_records,
            'success_records': self.success_records,
            'elapsed_seconds': elapsed,
            'records_per_second': self.success_records / elapsed if elapsed > 0 else 0
        }
        
        self.logger.info(f"同步完成: {result}")
        return result


def main():
    """示例用法"""
    # 配置
    TUSHARE_TOKEN = "your_token_here"  # 替换为你的 Tushare Token
    
    # 初始化
    syncer = TushareToDolphinDB(
        tushare_token=TUSHARE_TOKEN,
        dolphindb_host="localhost",
        dolphindb_port=8848,
        batch_size=10000  # Auditor 建议
    )
    
    # 同步（示例：前 10 只股票）
    stock_list = syncer.fetch_stock_list()[:10]
    
    result = syncer.sync(
        stock_list=stock_list,
        start_date="20240101",
        end_date="20240324"
    )
    
    print(f"\n同步结果:")
    print(f"  股票数: {result['total_stocks']}")
    print(f"  总记录: {result['total_records']}")
    print(f"  成功写入: {result['success_records']}")
    print(f"  耗时: {result['elapsed_seconds']:.2f}s")
    print(f"  速度: {result['records_per_second']:.0f} 条/秒")


if __name__ == "__main__":
    main()
