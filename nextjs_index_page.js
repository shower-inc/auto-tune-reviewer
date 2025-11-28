import Head from 'next/head';
import Link from 'next/link';
import { getSortedPostsData } from '../lib/posts';
import styles from '../styles/Home.module.css';

export async function getStaticProps() {
  const allPostsData = getSortedPostsData();
  return {
    props: {
      allPostsData,
    },
  };
}

export default function Home({ allPostsData }) {
  return (
    <div className={styles.container}>
      <Head>
        <title>AutoTune Reviewer - 音楽ブログ</title>
        <meta name="description" content="Spotifyの楽曲を自動レビューする音楽ブログ" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className={styles.main}>
        <h1 className={styles.title}>
          🎵 AutoTune Reviewer
        </h1>

        <p className={styles.description}>
          AIが生成する音楽レビューブログ
        </p>

        {allPostsData.length === 0 ? (
          <div className={styles.empty}>
            <p>まだ記事がありません。</p>
            <p>Spotify URLを追加して記事を生成してください。</p>
          </div>
        ) : (
          <div className={styles.grid}>
            {allPostsData.map(({ id, title, song_name, artist_name, created_at }) => (
              <Link href={`/posts/${id}`} key={id} className={styles.card}>
                <h2>{title}</h2>
                <p className={styles.meta}>
                  <span className={styles.artist}>{artist_name}</span>
                  <span className={styles.song}>{song_name}</span>
                </p>
                <p className={styles.date}>
                  {new Date(created_at).toLocaleDateString('ja-JP', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </p>
              </Link>
            ))}
          </div>
        )}
      </main>

      <footer className={styles.footer}>
        <p>Powered by Next.js × OpenAI × Spotify</p>
      </footer>
    </div>
  );
}
