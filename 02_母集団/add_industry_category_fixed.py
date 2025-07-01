#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
業種情報の追加と非上場企業の統合処理（修正版 - N/A企業を正しく検出）
"""

import pandas as pd
import numpy as np

def main():
    # ファイルパスの定義
    industry_file = "企業・業種区分"
    financial_file = "processed_financial_data.csv"
    output_file = "processed_financial_data_with_industry.csv"
    
    # 業種区分ファイルの読み込み（ヘッダーありで読み込み）
    print("業種区分ファイルを読み込み中...")
    # dtypeを指定してNoをstring型として読み込む
    industry_df = pd.read_csv(industry_file, delimiter='\t', dtype={'No': str})
    
    # 列名を確認
    print(f"列名: {industry_df.columns.tolist()}")
    
    # N/A以外の企業（上場企業）の業種情報を準備
    listed_companies = industry_df[industry_df['No'] != 'N/A'].copy()
    listed_companies['No_numeric'] = pd.to_numeric(listed_companies['No'], errors='coerce')
    
    # N/Aの企業（非上場企業）を抽出
    unlisted_companies = industry_df[industry_df['No'] == 'N/A'].copy()
    
    print(f"業種区分ファイルの企業数: {len(industry_df)}")
    print(f"上場企業数（業種区分ファイル）: {len(listed_companies)}")
    print(f"非上場企業数（業種区分ファイル）: {len(unlisted_companies)}")
    
    # 財務データファイルの読み込み
    print("財務データファイルを読み込み中...")
    # バックアップがある場合は元のファイルを使用
    try:
        financial_df = pd.read_csv(financial_file + '.backup', encoding='utf-8-sig')
        print("バックアップファイルから読み込みました")
    except:
        financial_df = pd.read_csv(financial_file, encoding='utf-8-sig')
    
    # 1. 既存の上場企業に業種情報を追加
    print("上場企業の業種情報をマージ中...")
    # コード列を数値型に変換
    financial_df['コード'] = pd.to_numeric(financial_df['コード'], errors='coerce')
    
    # 業種情報をマージ
    merged_df = financial_df.merge(
        listed_companies[['No_numeric', 'Scalar Segment']], 
        left_on='コード', 
        right_on='No_numeric', 
        how='left'
    )
    
    # 不要な列を削除し、列名を変更
    merged_df = merged_df.drop(columns=['No_numeric'])
    merged_df = merged_df.rename(columns={'Scalar Segment': '業種'})
    
    # 列の順序を調整（市場区分の後に業種を挿入）
    columns = list(merged_df.columns)
    # 業種列を市場区分の後に移動
    columns.remove('業種')
    idx = columns.index('市場区分') + 1
    columns.insert(idx, '業種')
    merged_df = merged_df[columns]
    
    # 2. 非上場企業のデータを追加
    print(f"非上場企業 {len(unlisted_companies)} 社を追加中...")
    
    # 非上場企業用のデータフレームを作成
    unlisted_data = []
    for _, row in unlisted_companies.iterrows():
        # 売上高を億円に変換（円から億円へ）
        sales_str = str(row.get('売上高(2022年時点)', ''))
        sales_value = np.nan
        if sales_str and sales_str.startswith('¥'):
            try:
                # ¥記号とカンマを除去して数値に変換
                sales_yen = float(sales_str.replace('¥', '').replace(',', ''))
                # 億円に変換
                sales_value = round(sales_yen / 100_000_000, 2)
            except:
                sales_value = np.nan
        
        unlisted_entry = {
            'コード': 'N/A',
            '企業名': row['銘柄'],
            '市場区分': '非上場',
            '業種': row['Scalar Segment'],
            '年度': '2022/03',  # 売上高データが2022年のため
            '売上高（億円）': sales_value,
            '営業利益（億円）': np.nan,
            '経常利益（億円）': np.nan,
            '純利益（億円）': np.nan,
            'EPS': np.nan,
            'ROE': np.nan,
            'ROA': np.nan
        }
        unlisted_data.append(unlisted_entry)
    
    unlisted_df = pd.DataFrame(unlisted_data)
    
    # 上場企業と非上場企業のデータを結合
    final_df = pd.concat([merged_df, unlisted_df], ignore_index=True)
    
    # 結果を保存
    print(f"結果を {output_file} に保存中...")
    final_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    # 元のファイルで置き換え
    import shutil
    shutil.move(output_file, financial_file)
    print(f"{financial_file} を更新しました")
    
    # サマリー情報を表示
    print("\n処理完了！")
    print(f"総企業数: {len(final_df)}")
    print(f"上場企業数: {len(merged_df)}")
    print(f"非上場企業数: {len(unlisted_df)}")
    print(f"\n業種別企業数:")
    print(final_df['業種'].value_counts().head(20))
    
    # 業種がマッチしなかった企業を確認
    no_industry = merged_df[merged_df['業種'].isna()]
    if len(no_industry) > 0:
        print(f"\n警告: {len(no_industry)} 社の上場企業で業種情報が見つかりませんでした")
    
    # 非上場企業のサンプルを表示
    if len(unlisted_df) > 0:
        print(f"\n追加された非上場企業のサンプル:")
        print(unlisted_df[['企業名', '業種', '売上高（億円）']].head(10))

if __name__ == "__main__":
    main()