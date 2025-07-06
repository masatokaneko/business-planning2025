import pandas as pd
from pathlib import Path

# ファイルパスの設定
BASE_DIR = Path(__file__).resolve().parent
ratio_path = BASE_DIR.parent / "00_raw_data" / "IT投資比率"
input_path = BASE_DIR / "processed_financial_data.csv"
output_path = BASE_DIR / "processed_financial_data_with_it.csv"

# 1. 業種別IT投資比率を読み込み
ratio_df = (
    pd.read_csv(
        ratio_path,
        sep="\t",  # タブ区切り
        comment="#",  # コメント行を無視
        header=None,
        names=["業種", "IT投資比率"]
    )
    .drop_duplicates("業種")  # 重複行を削除
)

# パーセンテージ文字を除去し、少数に変換
ratio_df["IT投資比率"] = (
    ratio_df["IT投資比率"].str.rstrip("%")
    .astype(float) / 100
).round(4)
ratio_mapping = ratio_df.set_index("業種")["IT投資比率"].to_dict()

# 2. 母集団データを読み込み
pop_df = pd.read_csv(input_path)

# 3. 比率をマッピングしてIT投資規模を計算
pop_df["IT投資比率"] = pop_df["業種"].map(ratio_mapping)

# 比率が存在しない業種は NaN になるので、0 で補完する
pop_df["IT投資比率"].fillna(0, inplace=True)

# 小数点以下4桁にそろえる
pop_df["IT投資比率"] = pop_df["IT投資比率"].round(4)

# 売上高（億円）×IT投資比率 で IT 投資規模（億円）を算定（億円未満は四捨五入）
pop_df["IT投資規模（億円）"] = (
    pop_df["売上高（億円）"] * pop_df["IT投資比率"]
).round().fillna(0).astype(int)

# 4. 結果を書き出し
pop_df.to_csv(output_path, index=False)

print(f"💾 IT投資規模を計算し、{output_path.name} に保存しました。") 