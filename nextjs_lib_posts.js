import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';
import { remark } from 'remark';
import html from 'remark-html';

const postsDirectory = path.join(process.cwd(), 'data/posts');

export function getAllPostIds() {
  try {
    // data/postsディレクトリが存在しない場合は空配列を返す
    if (!fs.existsSync(postsDirectory)) {
      return [];
    }

    const fileNames = fs.readdirSync(postsDirectory);
    
    // JSONファイルのみを対象にする
    const jsonFiles = fileNames.filter(fileName => fileName.endsWith('.json'));
    
    return jsonFiles.map(fileName => {
      return {
        params: {
          id: fileName.replace(/\.json$/, ''),
        },
      };
    });
  } catch (error) {
    console.error('Error reading posts directory:', error);
    return [];
  }
}

export async function getPostData(id) {
  try {
    // JSONファイルからメタデータを読み込む
    const jsonPath = path.join(postsDirectory, `${id}.json`);
    const jsonContent = fs.readFileSync(jsonPath, 'utf8');
    const metadata = JSON.parse(jsonContent);

    // Markdownファイルを読み込む
    const fullPath = path.join(postsDirectory, `${id}.md`);
    const fileContents = fs.readFileSync(fullPath, 'utf8');

    // gray-matterを使ってメタデータとコンテンツを解析
    const matterResult = matter(fileContents);

    // remarkを使ってMarkdownをHTMLに変換
    const processedContent = await remark()
      .use(html, { sanitize: false }) // iframeを許可するためsanitizeをfalseに
      .process(matterResult.content);
    const contentHtml = processedContent.toString();

    // メタデータとHTMLコンテンツを結合
    return {
      id,
      contentHtml,
      ...metadata,
    };
  } catch (error) {
    console.error(`Error reading post ${id}:`, error);
    return null;
  }
}

export function getSortedPostsData() {
  try {
    // data/postsディレクトリが存在しない場合は空配列を返す
    if (!fs.existsSync(postsDirectory)) {
      return [];
    }

    const fileNames = fs.readdirSync(postsDirectory);
    
    // JSONファイルのみを対象にする
    const jsonFiles = fileNames.filter(fileName => fileName.endsWith('.json'));
    
    const allPostsData = jsonFiles.map(fileName => {
      const id = fileName.replace(/\.json$/, '');
      const fullPath = path.join(postsDirectory, fileName);
      const fileContents = fs.readFileSync(fullPath, 'utf8');
      const metadata = JSON.parse(fileContents);

      return {
        id,
        ...metadata,
      };
    });

    // 日付順にソート
    return allPostsData.sort((a, b) => {
      if (a.created_at < b.created_at) {
        return 1;
      } else {
        return -1;
      }
    });
  } catch (error) {
    console.error('Error reading posts:', error);
    return [];
  }
}
