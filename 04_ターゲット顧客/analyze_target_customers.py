import pandas as pd
import numpy as np

# Read the CSV file
df = pd.read_csv('../02_母集団/processed_financial_data_with_it.csv')

# Define tier criteria
def classify_revenue_tier(revenue):
    if revenue >= 10000:  # 1兆円以上
        return 'Tier1'
    elif revenue >= 3000:  # 3千億円以上
        return 'Tier2'
    else:
        return 'Tier3'

def classify_it_investment_tier(it_investment):
    if it_investment >= 300:  # 300億円以上
        return 'Tier1'
    elif it_investment >= 100:  # 100億円以上
        return 'Tier2'
    else:
        return 'Tier3'

# Apply classification
df['売上高Tier'] = df['売上高（億円）'].apply(classify_revenue_tier)
df['IT投資Tier'] = df['IT投資規模（億円）'].apply(classify_it_investment_tier)

# Filter for Tier1-2 x Tier1-2 companies
target_companies = df[
    (df['売上高Tier'].isin(['Tier1', 'Tier2'])) & 
    (df['IT投資Tier'].isin(['Tier1', 'Tier2']))
]

# Create segment labels with clear prefixes
target_companies['セグメント'] = '売上' + target_companies['売上高Tier'] + ' × IT投資' + target_companies['IT投資Tier']

# Analyze by industry and segment
industry_segment_pivot = pd.crosstab(
    target_companies['業種'], 
    target_companies['セグメント'],
    margins=True,
    margins_name='合計'
)

# Get unique industries (excluding '合計')
industries = [idx for idx in industry_segment_pivot.index if idx != '合計']

# Create summary dataframe
industry_summary_list = []
for industry in industries:
    row_data = {
        '業種': industry,
        '売上Tier1×IT投資Tier1': industry_segment_pivot.loc[industry, '売上Tier1 × IT投資Tier1'] if '売上Tier1 × IT投資Tier1' in industry_segment_pivot.columns else 0,
        '売上Tier1×IT投資Tier2': industry_segment_pivot.loc[industry, '売上Tier1 × IT投資Tier2'] if '売上Tier1 × IT投資Tier2' in industry_segment_pivot.columns else 0,
        '売上Tier2×IT投資Tier1': industry_segment_pivot.loc[industry, '売上Tier2 × IT投資Tier1'] if '売上Tier2 × IT投資Tier1' in industry_segment_pivot.columns else 0,
        '売上Tier2×IT投資Tier2': industry_segment_pivot.loc[industry, '売上Tier2 × IT投資Tier2'] if '売上Tier2 × IT投資Tier2' in industry_segment_pivot.columns else 0,
        '合計': industry_segment_pivot.loc[industry, '合計']
    }
    industry_summary_list.append(row_data)

industry_summary = pd.DataFrame(industry_summary_list)
industry_summary = industry_summary.sort_values('合計', ascending=False)

# Add total row
total_row = {
    '業種': '合計',
    '売上Tier1×IT投資Tier1': industry_summary['売上Tier1×IT投資Tier1'].sum(),
    '売上Tier1×IT投資Tier2': industry_summary['売上Tier1×IT投資Tier2'].sum(),
    '売上Tier2×IT投資Tier1': industry_summary['売上Tier2×IT投資Tier1'].sum(),
    '売上Tier2×IT投資Tier2': industry_summary['売上Tier2×IT投資Tier2'].sum(),
    '合計': industry_summary['合計'].sum()
}
industry_summary = pd.concat([industry_summary, pd.DataFrame([total_row])], ignore_index=True)

# Save industry summary with segments
industry_summary.to_csv('業種別_売上Tier1-2×IT投資Tier1-2企業数.csv', index=False, encoding='utf-8-sig')

print("=== 業種別 売上Tier1-2 × IT投資Tier1-2 企業数分析 ===")
print(f"総企業数: {len(target_companies)}社")
print("\n売上高Tier定義: Tier1(1兆円以上), Tier2(3千億円以上)")
print("IT投資Tier定義: Tier1(300億円以上), Tier2(100億円以上)")
print("\n業種別・セグメント別内訳:")
print(industry_summary.to_string(index=False))

# Create detailed company list by industry
detailed_list = []
for industry in target_companies['業種'].unique():
    industry_companies = target_companies[target_companies['業種'] == industry].sort_values('売上高（億円）', ascending=False)
    
    for _, company in industry_companies.iterrows():
        detailed_list.append({
            '業種': industry,
            '企業名': company['企業名'],
            'コード': company['コード'],
            '売上高Tier': company['売上高Tier'],
            'IT投資Tier': company['IT投資Tier'],
            '売上高（億円）': company['売上高（億円）'],
            'IT投資規模（億円）': company['IT投資規模（億円）'],
            'IT投資比率': company['IT投資比率']
        })

# Create DataFrame and save
detailed_df = pd.DataFrame(detailed_list)
detailed_df = detailed_df.sort_values(['業種', '売上高（億円）'], ascending=[True, False])
detailed_df.to_csv('売上Tier1-2×IT投資Tier1-2企業詳細リスト.csv', index=False, encoding='utf-8-sig')

print(f"\n\nファイル出力完了:")
print("1. 業種別_売上Tier1-2×IT投資Tier1-2企業数.csv - 業種ごとの企業数集計")
print("2. 売上Tier1-2×IT投資Tier1-2企業詳細リスト.csv - 企業詳細情報")

# Additional analysis: Show top companies in each tier combination
print("\n\n=== セグメント別 代表企業 ===")
for revenue_tier in ['Tier1', 'Tier2']:
    for it_tier in ['Tier1', 'Tier2']:
        segment_companies = target_companies[
            (target_companies['売上高Tier'] == revenue_tier) & 
            (target_companies['IT投資Tier'] == it_tier)
        ]
        if len(segment_companies) > 0:
            print(f"\n売上{revenue_tier} × IT投資{it_tier}: {len(segment_companies)}社")
            top_companies = segment_companies.nlargest(5, '売上高（億円）')[['企業名', '業種', '売上高（億円）', 'IT投資規模（億円）']]
            for _, company in top_companies.iterrows():
                print(f"  - {company['企業名']} ({company['業種']}) - 売上高: {company['売上高（億円）']:,.0f}億円, IT投資: {company['IT投資規模（億円）']:,.0f}億円")