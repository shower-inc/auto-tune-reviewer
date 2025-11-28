import csv
import os
import json
import re
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# OpenAI APIの設定（環境変数から取得を推奨）
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-api-key-here')
OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'

def load_csv(filepath='input.csv'):
    """CSVファイルを読み込み、処理フラグが'NEW'の行のみを抽出"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        new_rows = [row for row in rows if row.get('処理フラグ', '').strip() == 'NEW']
        print(f"✓ CSV読み込み完了: 全{len(rows)}件中、処理対象{len(new_rows)}件")
        return rows, new_rows
    except FileNotFoundError:
        print(f"✗ エラー: {filepath} が見つかりません")
        return [], []

def extract_spotify_info(spotify_url):
    """SpotifyのURLから曲情報とiframe埋め込みコードを抽出"""
    try:
        # SpotifyのURLからトラックIDを抽出
        match = re.search(r'track/([a-zA-Z0-9]+)', spotify_url)
        if not match:
            return None, None, None
        
        track_id = match.group(1)
        
        # Spotify埋め込みコードを生成
        iframe_code = f'<iframe style="border-radius:12px" src="https://open.spotify.com/embed/track/{track_id}?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'
        
        # Webページから曲名とアーティスト名を取得
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(spotify_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # メタタグから情報を取得
        title_tag = soup.find('meta', property='og:title')
        description_tag = soup.find('meta', property='og:description')
        
        song_name = title_tag['content'] if title_tag else f"Track {track_id}"
        artist_name = description_tag['content'].split('·')[0].strip() if description_tag else "Unknown Artist"
        
        print(f"  ✓ 抽出成功: {song_name} / {artist_name}")
        return song_name, artist_name, iframe_code
        
    except Exception as e:
        print(f"  ✗ 抽出エラー: {str(e)}")
        # フォールバック: 埋め込みコードのみ返す
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
        
        # JSONを抽出（マークダウンのコードブロックを除去）
        content = re.sub(r'```json\n?|\n?```', '', content).strip()
        parsed = json.loads(content)
        
        print(f"  ✓ LLM生成完了")
        return parsed
        
    except Exception as e:
        print(f"  ✗ LLM生成エラー: {str(e)}")
        return {
            'title': f'{song_name} - {artist_name}',
            'blog_content': f'{artist_name}の「{song_name}」をご紹介します。\n\nこの楽曲は、ぜひ聴いていただきたい一曲です。',
            'sns_post': f'🎵 {song_name} / {artist_name}\n\n#音楽 #NowPlaying'
        }

def create_markdown_file(record_id, title, blog_content, sns_post, iframe_code):
    """Markdown形式のブログ記事ファイルを生成"""
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    markdown_content = f"""# {title}

{blog_content}

## Spotifyで聴く

{iframe_code}

---

### SNS投稿用

{sns_post}
"""
    
    filepath = output_dir / f'post_{record_id}.md'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"  ✓ 記事ファイル生成: {filepath}")
    return filepath

def update_csv_flag(filepath, all_rows, processed_ids):
    """処理済みレコードのフラグを'DONE'に更新"""
    for row in all_rows:
        if row['ID'] in processed_ids:
            row['処理フラグ'] = 'DONE'
    
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        fieldnames = all_rows[0].keys() if all_rows else []
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    
    print(f"✓ CSVファイル更新完了: {len(processed_ids)}件をDONEに変更")

def main():
    """メイン処理"""
    print("=" * 60)
    print("AutoTune Reviewer - 自動ブログ記事生成システム")
    print("=" * 60)
    
    # 1. CSV読み込み
    all_rows, new_rows = load_csv('input.csv')
    if not new_rows:
        print("\n処理対象のレコードがありません。")
        return
    
    processed_ids = []
    
    # 各レコードを処理
    for row in new_rows:
        record_id = row['ID']
        spotify_url = row['Spotify_URL']
        
        print(f"\n[ID: {record_id}] 処理開始")
        print(f"  URL: {spotify_url}")
        
        # 2. 情報抽出
        song_name, artist_name, iframe_code = extract_spotify_info(spotify_url)
        if not iframe_code:
            print(f"  ✗ スキップ: 情報抽出に失敗しました")
            continue
        
        # 3. コンテンツ生成
        content = generate_content_with_llm(song_name, artist_name)
        
        # 4. 記事ファイル生成
        create_markdown_file(
            record_id,
            content['title'],
            content['blog_content'],
            content['sns_post'],
            iframe_code
        )
        
        processed_ids.append(record_id)
    
    # 5. フラグ更新
    if processed_ids:
        update_csv_flag('input.csv', all_rows, processed_ids)
    
    print("\n" + "=" * 60)
    print(f"✓ 処理完了: {len(processed_ids)}件の記事を生成しました")
    print("=" * 60)

if __name__ == '__main__':
    main()
