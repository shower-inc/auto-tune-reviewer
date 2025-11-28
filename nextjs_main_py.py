import csv
import os
import json
import re
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# OpenAI APIの設定（環境変数から取得）
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'

# 出力ディレクトリの設定
OUTPUT_DIR = Path('data/posts')
INPUT_CSV = Path('scripts/input.csv')

def load_csv():
    """CSVファイルを読み込み、処理フラグが'NEW'の行のみを抽出"""
    try:
        with open(INPUT_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        new_rows = [row for row in rows if row.get('処理フラグ', '').strip() == 'NEW']
        print(f"✓ CSV読み込み完了: 全{len(rows)}件中、処理対象{len(new_rows)}件")
        return rows, new_rows
    except FileNotFoundError:
        print(f"✗ エラー: {INPUT_CSV} が見つかりません")
        return [], []

def extract_spotify_info(spotify_url):
    """SpotifyのURLから曲情報とiframe埋め込みコードを抽出"""
    try:
        match = re.search(r'track/([a-zA-Z0-9]+)', spotify_url)
        if not match:
            return None, None, None
        
        track_id = match.group(1)
        iframe_code = f'<iframe style="border-radius:12px" src="https://open.spotify.com/embed/track/{track_id}?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(spotify_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        title_tag = soup.find('meta', property='og:title')
        description_tag = soup.find('meta', property='og:description')
        
        song_name = title_tag['content'] if title_tag else f"Track {track_id}"
        artist_name = description_tag['content'].split('·')[0].strip() if description_tag else "Unknown Artist"
        
        print(f"  ✓ 抽出成功: {song_name} / {artist_name}")
        return song_name, artist_name, iframe_code
        
    except Exception as e:
        print(f"  ✗ 抽出エラー: {str(e)}")
        try:
            match = re.search(r'track/([a-zA-Z0-9]+)', spotify_url)
            if match:
                track_id = match.group(1)
                iframe_code = f'<iframe style="border-radius:12px" src="https://open.spotify.com/embed/track/{track_id}?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'
                return "曲名取得失敗", "アーティスト名取得失敗", iframe_code
        except:
            pass
        return None, None, None

def generate_content_with_llm(song_name, artist_name):
    """OpenAI APIを使用してブログ記事とSNS投稿を生成"""
    prompt = f"""あなたは専門の音楽ライターです。以下の曲について、読者が興味を持つような魅力的なブログ紹介文（日本語で800字程度）と、SNS（X/Twitter）用の投稿文（ハッシュタグ付き、100文字以内）を生成してください。

[曲名]: {song_name}
[アーティスト名]: {artist_name}

以下のJSON形式で出力してください:
{{
  "title": "記事タイトル",
  "blog_content": "ブログ本文（800字程度）",
  "sns_post": "SNS投稿文（100文字以内、ハッシュタグ付き）"
}}"""

    if not OPENAI_API_KEY:
        print(f"  ⚠ APIキー未設定: ダミーデータを使用")
        return {
            'title': f'{song_name} - {artist_name}',
            'blog_content': f'{artist_name}の「{song_name}」をご紹介します。\n\nこの楽曲は、心に響く素晴らしいメロディと歌詞が特徴です。ぜひ聴いていただきたい一曲です。',
            'sns_post': f'🎵 {song_name} / {artist_name}\n\n#音楽 #NowPlaying'
        }

    try:
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'gpt-4o',
            'messages': [
                {'role': 'system', 'content': 'あなたは音楽に詳しいプロのライターです。JSON形式で正確に出力してください。'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.7,
            'max_tokens': 2000
        }
        
        response = requests.post(OPENAI_API_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        content = re.sub(r'```json\n?|\n?```', '', content).strip()
        parsed = json.loads(content)
        
        print(f"  ✓ LLM生成完了")
        return parsed
        
    except Exception as e:
        print(f"  ✗ LLM生成エラー: {str(e)}")
        return {
            'title': f'{song_name} - {artist_name}',
            'blog_content': f'{artist_name}の「{song_name}」をご紹介します。\n\nこの楽曲は、心に響く素晴らしいメロディと歌詞が特徴です。ぜひ聴いていただきたい一曲です。',
            'sns_post': f'🎵 {song_name} / {artist_name}\n\n#音楽 #NowPlaying'
        }

def create_post_files(record_id, title, blog_content, sns_post, iframe_code, song_name, artist_name, spotify_url):
    """Markdownファイルとメタデータ（JSON）を生成"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Markdownファイルの作成
    markdown_content = f"""# {title}

{blog_content}

## Spotifyで聴く

{iframe_code}

---

### SNS投稿用

{sns_post}
"""
    
    md_filepath = OUTPUT_DIR / f'{record_id}.md'
    with open(md_filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    # メタデータ（JSON）の作成
    metadata = {
        'id': record_id,
        'title': title,
        'song_name': song_name,
        'artist_name': artist_name,
        'spotify_url': spotify_url,
        'content': blog_content,
        'iframe_code': iframe_code,
        'sns_post': sns_post,
        'created_at': datetime.now().isoformat(),
    }
    
    json_filepath = OUTPUT_DIR / f'{record_id}.json'
    with open(json_filepath, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ ファイル生成: {md_filepath}, {json_filepath}")
    return md_filepath, json_filepath

def update_csv_flag(all_rows, processed_ids):
    """処理済みレコードのフラグを'DONE'に更新"""
    for row in all_rows:
        if row['ID'] in processed_ids:
            row['処理フラグ'] = 'DONE'
    
    with open(INPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        fieldnames = all_rows[0].keys() if all_rows else []
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    
    print(f"✓ CSVファイル更新完了: {len(processed_ids)}件をDONEに変更")

def main():
    """メイン処理"""
    print("=" * 60)
    print("AutoTune Reviewer - 記事生成スクリプト（Next.js版）")
    print("=" * 60)
    
    all_rows, new_rows = load_csv()
    if not new_rows:
        print("\n処理対象のレコードがありません。")
        return
    
    processed_ids = []
    
    for row in new_rows:
        record_id = row['ID']
        spotify_url = row['Spotify_URL']
        
        print(f"\n[ID: {record_id}] 処理開始")
        print(f"  URL: {spotify_url}")
        
        song_name, artist_name, iframe_code = extract_spotify_info(spotify_url)
        if not iframe_code:
            print(f"  ✗ スキップ: 情報抽出に失敗しました")
            continue
        
        content = generate_content_with_llm(song_name, artist_name)
        
        create_post_files(
            record_id,
            content['title'],
            content['blog_content'],
            content['sns_post'],
            iframe_code,
            song_name,
            artist_name,
            spotify_url
        )
        
        processed_ids.append(record_id)
    
    if processed_ids:
        update_csv_flag(all_rows, processed_ids)
    
    print("\n" + "=" * 60)
    print(f"✓ 処理完了: {len(processed_ids)}件の記事を生成しました")
    print("=" * 60)

if __name__ == '__main__':
    main()
