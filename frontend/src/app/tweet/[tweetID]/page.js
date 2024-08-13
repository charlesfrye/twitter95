import { getTweet } from '../../../services/database';
import Tweet from '../../../components/Tweet';

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

export default async function TweetPage({ params }) {
  // serverside render the tweet
  const tweet = await getTweet(params.tweetID);

  return (
    <div className="banner align-middle mt-4">
      <Tweet tweet={tweet} showStats={true} />
    </div>
  );
}