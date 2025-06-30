import pandas as pd
import numpy as np
from datetime import datetime

def load_company_master(master_file):
    """
    東証の企業マスターデータを読み込み
    """
    master_df = pd.read_csv(master_file, encoding='utf-8')
    # コードと銘柄名の辞書を作成
    company_dict = dict(zip(master_df['コード'].astype(str), master_df['銘柄名']))
    # ETF/ETN/REITを除外するための市場区分情報も保持
    market_dict = dict(zip(master_df['コード'].astype(str), master_df['市場・商品区分']))
    return company_dict, market_dict

def process_financial_data(input_file, output_file, master_file):
    """
    財務データを処理して最新年度のデータのみを抽出
    """
    # 企業マスターデータを読み込み
    company_names, market_types = load_company_master(master_file)
    
    # CSVファイルを読み込み（BOM付きUTF-8に対応、ヘッダーは3行目）
    df = pd.read_csv(input_file, encoding='utf-8-sig', skiprows=2)
    
    # データクリーニング
    df['コード'] = df['コード'].astype(str)
    
    # 年度を標準化（YYYY/MM形式に統一）
    df['年度'] = pd.to_datetime(df['年度'], format='%Y/%m', errors='coerce')
    
    # 数値フィールドを数値型に変換
    numeric_columns = ['売上高', '営業利益', '経常利益', '純利益', 'EPS', 'ROE', 'ROA']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 各企業の最新年度データのみを抽出
    latest_data = df.sort_values(['コード', '年度']).groupby('コード').last().reset_index()
    
    # 企業名を追加
    latest_data['企業名'] = latest_data['コード'].map(lambda x: company_names.get(x, f'不明（コード：{x}）'))
    
    # 市場区分を追加
    latest_data['市場区分'] = latest_data['コード'].map(lambda x: market_types.get(x, '不明'))
    
    # ETF、ETN、REITを除外（内国株式のみを抽出）
    latest_data = latest_data[latest_data['市場区分'].str.contains('内国株式', na=False)]
    
    # 売上高でソート（降順）
    latest_data = latest_data.sort_values('売上高', ascending=False)
    
    # 出力用カラムの選択と並び替え
    output_columns = ['コード', '企業名', '市場区分', '年度', '売上高', '営業利益', '経常利益', '純利益', 'EPS', 'ROE', 'ROA']
    latest_data = latest_data[output_columns]
    
    # 金額を億円単位に変換（読みやすさのため）
    amount_columns = ['売上高', '営業利益', '経常利益', '純利益']
    for col in amount_columns:
        latest_data[f'{col}（億円）'] = (latest_data[col] / 100000000).round(0).astype('Int64')
    
    # 最終的な出力データフレーム
    final_columns = ['コード', '企業名', '市場区分', '年度', '売上高（億円）', '営業利益（億円）', 
                    '経常利益（億円）', '純利益（億円）', 'EPS', 'ROE', 'ROA']
    final_data = latest_data.copy()
    final_data = final_data.rename(columns={
        '売上高': '売上高（原値）',
        '営業利益': '営業利益（原値）',
        '経常利益': '経常利益（原値）',
        '純利益': '純利益（原値）'
    })
    
    # 年度を文字列形式に戻す
    final_data['年度'] = final_data['年度'].dt.strftime('%Y/%m')
    
    # CSVとして保存
    final_data[final_columns].to_csv(output_file, index=False, encoding='utf-8-sig')
    
    # サマリー統計の表示
    print(f"処理済みレコード数: {len(final_data)}")
    print(f"最大売上高: {final_data['売上高（億円）'].max():,} 億円")
    print(f"最小売上高: {final_data['売上高（億円）'].min():,} 億円")
    
    return final_data[final_columns]

if __name__ == "__main__":
    input_file = "/Users/kanekomasato/business-planning2025/raw_data/fy-profit-and-loss.csv"
    master_file = "/Users/kanekomasato/business-planning2025/raw_data/data_j.xls - Sheet1.csv"
    output_file = "/Users/kanekomasato/business-planning2025/processed_financial_data.csv"
    
    result = process_financial_data(input_file, output_file, master_file)
    print(f"\n処理完了: {output_file}")
    print("\n上位10社の売上高:")
    print(result.head(10).to_string(index=False))