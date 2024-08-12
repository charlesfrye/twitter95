// src/app/tweet/[tweetId]/page.js
import TweetPage from '../../../components/TweetPage';

// // TODO: generate metadata server-side
// export async function generateMetadata({ params }) {
//   const tweetData = await getTweetData(params.tweetId);
//   return {
//     title: `Tweet by ${tweetData.author}`,
//     description: tweetData.content,
//     openGraph: {
//       images: [tweetData.ogImage],
//     },
//   };
// }

export default async function Tweet({ params }) {
  return <TweetPage tweetID={params.tweetID} />;
}