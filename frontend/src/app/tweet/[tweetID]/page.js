import { getTweet } from '../../../services/database';
import TweetPage from '../../../components/TweetPage';

export async function generateMetadata({ params }) {
  const tweet = await getTweet(params.tweetID);
  return {
    title: `Tweet by ${tweet.author.user_name} on Twitter '95`,
    description: tweet.text,
    openGraph: {
      title: `Tweet by ${tweet.author.user_name} on Twitter '95`,
      description: tweet.text,
    },
  };
}

export default async function Tweet({ params }) {
  return <TweetPage tweetID={params.tweetID} />;
}