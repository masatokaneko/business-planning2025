import pandas as pd
import numpy as np

# Read the CSV file
df = pd.read_csv('processed_financial_data_with_it.csv')

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

# Create tier matrix
tier_matrix = pd.crosstab(df['売上高Tier'], df['IT投資Tier'], margins=True, margins_name='合計')

print("=== 顧客Tierマトリックス分析 ===")
print("\n売上高とIT投資額によるTier分類:")
print("- 売上高: Tier1(1兆円以上), Tier2(3千億円以上), Tier3(3千億円未満)")
print("- IT投資額: Tier1(300億円以上), Tier2(100億円以上), Tier3(100億円未満)")
print("\n【企業数マトリックス】")
print(tier_matrix)

# Calculate percentages
total_companies = len(df)
print(f"\n【構成比率（％）】")
percentage_matrix = (tier_matrix / total_companies * 100).round(1)
print(percentage_matrix)

# Detailed analysis for each segment
print("\n【詳細分析】")
for revenue_tier in ['Tier1', 'Tier2', 'Tier3']:
    for it_tier in ['Tier1', 'Tier2', 'Tier3']:
        companies = df[(df['売上高Tier'] == revenue_tier) & (df['IT投資Tier'] == it_tier)]
        if len(companies) > 0:
            print(f"\n売上高{revenue_tier} × IT投資{it_tier}: {len(companies)}社")
            print(f"  代表企業: {', '.join(companies['企業名'].head(3).tolist())}")
            avg_revenue = companies['売上高（億円）'].mean()
            avg_it = companies['IT投資規模（億円）'].mean()
            print(f"  平均売上高: {avg_revenue:,.0f}億円")
            print(f"  平均IT投資額: {avg_it:,.0f}億円")