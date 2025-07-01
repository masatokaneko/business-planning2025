#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
N/A企業の検出問題をデバッグ
"""

import pandas as pd

# ファイルを読み込み
df = pd.read_csv("企業・業種区分", delimiter='\t', dtype={'No': str})

print(f"総行数: {len(df)}")
print(f"列名: {df.columns.tolist()}")
print(f"\nNo列のユニークな値の数: {df['No'].nunique()}")
print(f"No列の最初の10個の値: {df['No'].head(10).tolist()}")

# N/Aを含む行を検索
na_rows = df[df['No'] == 'N/A']
print(f"\nN/A企業の数: {len(na_rows)}")

if len(na_rows) == 0:
    # 他の可能性を試す
    print("\n'N/A'で見つからないので、他の可能性を確認...")
    
    # 文字列にN/Aを含む行
    contains_na = df[df['No'].str.contains('N/A', na=False)]
    print(f"'N/A'を含む行数: {len(contains_na)}")
    
    # NaNの行
    nan_rows = df[df['No'].isna()]
    print(f"NaN行数: {len(nan_rows)}")
    
    # 空文字列の行
    empty_rows = df[df['No'] == '']
    print(f"空文字列行数: {len(empty_rows)}")
    
    # No列の値の分布を確認
    print(f"\nNo列の値の分布（上位20）:")
    print(df['No'].value_counts().head(20))