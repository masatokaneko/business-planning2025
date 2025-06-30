import pandas as pd
import numpy as np

def compare_financial_data():
    """
    ClaudeとGeminiが作成した財務データの比較分析
    """
    # ファイルの読み込み
    claude_df = pd.read_csv('/Users/kanekomasato/business-planning2025/Claude_financial_data.csv', encoding='utf-8-sig')
    gemini_df = pd.read_csv('/Users/kanekomasato/business-planning2025/Gemini_financial_data.csv', encoding='utf-8-sig')
    
    print("=== ファイル構造の比較 ===")
    print(f"Claude作成: {len(claude_df)}社, カラム数: {len(claude_df.columns)}")
    print(f"Gemini作成: {len(gemini_df)}社, カラム数: {len(gemini_df.columns)}")
    print(f"\nClaudeのカラム: {list(claude_df.columns)}")
    print(f"Geminiのカラム: {list(gemini_df.columns)}")
    
    # Geminiのデータを億円単位に変換（比較のため）
    # まず数値に変換
    gemini_df['売上高'] = pd.to_numeric(gemini_df['売上高'], errors='coerce')
    gemini_df['営業利益'] = pd.to_numeric(gemini_df['営業利益'], errors='coerce')
    gemini_df['純利益'] = pd.to_numeric(gemini_df['純利益'], errors='coerce')
    
    gemini_df['売上高（億円）'] = (gemini_df['売上高'] / 100000000).round(0).astype('Int64')
    gemini_df['営業利益（億円）'] = (gemini_df['営業利益'] / 100000000).round(0).astype('Int64')
    gemini_df['純利益（億円）'] = (gemini_df['純利益'] / 100000000).round(0).astype('Int64')
    
    # コードを文字列に統一
    claude_df['コード'] = claude_df['コード'].astype(str)
    gemini_df['コード'] = gemini_df['コード'].astype(str)
    
    # 共通企業の抽出
    common_codes = set(claude_df['コード']) & set(gemini_df['コード'])
    print(f"\n=== 共通企業数: {len(common_codes)} ===")
    
    # 両方のデータセットにある企業のみを抽出
    claude_common = claude_df[claude_df['コード'].isin(common_codes)].sort_values('コード')
    gemini_common = gemini_df[gemini_df['コード'].isin(common_codes)].sort_values('コード')
    
    # 重要な差異の分析
    print("\n=== 主要企業の数値比較（売上高上位10社） ===")
    
    # 売上高上位10社を比較
    top_companies = claude_df.nlargest(10, '売上高（億円）')[['コード', '企業名']]
    
    comparison_results = []
    for _, company in top_companies.iterrows():
        code = company['コード']
        name = company['企業名']
        
        claude_data = claude_df[claude_df['コード'] == code].iloc[0] if code in claude_df['コード'].values else None
        gemini_data = gemini_df[gemini_df['コード'] == code].iloc[0] if code in gemini_df['コード'].values else None
        
        if claude_data is not None and gemini_data is not None:
            result = {
                'コード': code,
                '企業名': name,
                'Claude売上高': claude_data['売上高（億円）'],
                'Gemini売上高': gemini_data['売上高（億円）'],
                '売上高差異': claude_data['売上高（億円）'] - gemini_data['売上高（億円）'],
                'Claude営業利益': claude_data['営業利益（億円）'],
                'Gemini営業利益': gemini_data['営業利益（億円）'],
                'Claude純利益': claude_data['純利益（億円）'],
                'Gemini純利益': gemini_data['純利益（億円）']
            }
            comparison_results.append(result)
    
    comparison_df = pd.DataFrame(comparison_results)
    if not comparison_df.empty:
        print(comparison_df.to_string(index=False))
    
    # データの包括性の比較
    print("\n=== データの包括性 ===")
    claude_only = set(claude_df['コード']) - set(gemini_df['コード'])
    gemini_only = set(gemini_df['コード']) - set(claude_df['コード'])
    
    print(f"Claudeのみに存在: {len(claude_only)}社")
    print(f"Geminiのみに存在: {len(gemini_only)}社")
    
    # カラムの違い
    print("\n=== カラムの差異 ===")
    print("Claudeのみのカラム:", [col for col in claude_df.columns if col not in ['コード', '企業名', '年度', '売上高（億円）', '営業利益（億円）', '純利益（億円）']])
    print("Geminiのみのカラム:", [col for col in gemini_df.columns if col not in ['コード', '銘柄名', '年度', '売上高', '営業利益', '純利益']])
    
    # 年度フォーマットの違い
    print("\n=== 年度フォーマットの違い ===")
    print(f"Claude年度例: {claude_df['年度'].iloc[0]}")
    print(f"Gemini年度例: {gemini_df['年度'].iloc[0]}")
    
    # ETF/ファンドの扱い
    print("\n=== ETF/ファンドの扱い ===")
    claude_etf_count = len(claude_df[claude_df['市場区分'].str.contains('ETF|ETN', na=False)])
    print(f"ClaudeのETF/ETN数: {claude_etf_count}")
    print(f"Geminiの全企業数: {len(gemini_df)} (ETF除外の有無は不明)")
    
    return comparison_df

if __name__ == "__main__":
    compare_financial_data()