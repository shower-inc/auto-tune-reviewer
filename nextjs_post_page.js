import Head from 'next/head';
import Link from 'next/link';
import { getAllPostIds, getPostData } from '../../lib/posts';
import styles from '../../styles/Post.module.css';

export async function getStaticPaths() {
  const paths = getAllPostIds();
  return {
    paths,
    fallback: false,
  };
}

export async function getStaticProps({ params }) {
  const postData = await getPostData(params.id);
  
  if (!postData) {
    return {
      notFound: true,
    };
  }
  
  return {
    props: {
      postData,
    },
  };
}

export default function Post({ postData }) {
  return (
    <div className={styles.container}>
      <Head>
        <title>{postData.title} | AutoTune Reviewer</title>
        <meta name="description" content={postData.content.substring(0, 160)} />
        <meta property="og:title" content={postData.title} />
        <meta property="og:description" content={postData.content.substring(0, 160)} />
      </Head>

      <main className={styles.main}>
        <Link href="/" className={styles.backLink}>
          ← トップページに戻る
        </Link>

        <article className={styles.article}>
          <header className={styles.header}>
            <h1 className={styles.title}>{postData.title}</h1>
            <div className={styles.meta}>
              <span className={styles.artist}>{postData.artist_name}</span>
              <span className={styles.separator}>•</span>
              <span className={styles.song}>{postData.song_name}</span>
            </div>
            <time className={styles.date}>
              {new Date(postData.created_at).toLocaleDateString('ja-JP', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </time>
          </header>

          <div 
            className={styles.content}
            dangerouslySetInnerHTML={{ __html: postData.contentHtml }}
          />

          <div className={styles.snsSection}>
            <h3>SNS投稿用</h3>
            <div className={styles.snsPost}>
              {postData.sns_post}
            </div>
            <button 
              className={styles.copyButton}
              onClick={() => {
                navigator.clipboard.writeText(postData.sns_post);
                alert('コピーしました！');
              }}
            >
              📋 コピー
            </button>
          </div>
        </article>
      </main>

      <footer className={styles.footer}>
        <Link href="/">← 記事一覧に戻る</Link>
      </footer>
    </div>
  );
}
