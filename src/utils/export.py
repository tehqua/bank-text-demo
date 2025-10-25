from pathlib import Path
import json
from datetime import datetime

def export_to_csv(df_spark, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df_spark.toPandas().to_csv(output_path, index=False, encoding='utf-8-sig')
    return output_path

def export_summary_to_json(summary_dict, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    summary_dict["exported_at"] = datetime.now().isoformat()

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(summary_dict, f, ensure_ascii=False, indent=2)

    return output_path

def export_summary_to_markdown(summary_dict, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    md_lines = [
        f"# Summary Report",
        f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        f"## Overview",
        f"- Total comments: {summary_dict.get('total_comments', 0)}",
        f"- Unique topics: {summary_dict.get('unique_topics', 0)}",
        f"- Average sentiment: {summary_dict.get('avg_sentiment', 0):.2f}\n",
        f"## Top Issues"
    ]

    if 'top_issues' in summary_dict:
        for issue in summary_dict['top_issues']:
            md_lines.append(f"- {issue}")

    md_lines.append(f"\n## Sentiment Distribution")
    if 'sentiment_dist' in summary_dict:
        for label, count in summary_dict['sentiment_dist'].items():
            md_lines.append(f"- {label}: {count}")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))

    return output_path
