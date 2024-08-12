// src/app/tweet/[tweetId]/page.js
import { getTweetData } from '../../../services/database';
import TweetPageClient from '../../../components/TweetPageClient';

export async function generateMetadata({ params }) {
  const tweetData = await getTweetData(params.tweetId);
  return {
    title: `Tweet by ${tweetData.author}`,
    description: tweetData.content,
    openGraph: {
      images: [tweetData.ogImage],
    },
  };
}

export default async function Tweet({ params }) {
  const tweetData = await getTweetData(params.tweetId);
  return <TweetPageClient tweetData={tweetData} />;
}