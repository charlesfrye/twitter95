import { ImageResponse } from 'next/og'
import { getTweet } from '../../../services/database';

export const runtime = 'edge'

export const alt = 'Tweet Image'
export const size = {
  width: 800,
  height: 450,
}
export const contentType = 'image/png'

function formatFakeTime(fakeTimeStr) {
    const date = new Date(fakeTimeStr);
    return new Intl.DateTimeFormat("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    }).format(date);
}

export default async function Image({ params }) {
    const tweetID = params.tweetID;
    const tweet = await getTweet(tweetID);

    const fontData = await fetch(new URL('../../../../public/fonts/ms_sans_serif.ttf', import.meta.url),).then(res => res.arrayBuffer())
    
    try {
        return new ImageResponse(
            (
            <div
                style={{
                    width: '100%',
                    height: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    backgroundColor: '#000000',
                    padding: '20px',
                    fontFamily: '"MS Sans Serif"',
                }}
            >
                <div style={{
                    width: '90%',
                    maxWidth: '700px',
                    display: 'flex',
                    flexDirection: 'column',
                    backgroundColor: '#c0c0c0',
                    border: '2px solid #d3d3d3',
                    overflow: 'hidden',
                    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                }}>
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        padding: '15px',
                        borderBottom: '2px solid #a9a9a9',
                    }}>
                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            flex: 1,
                        }}>
                            <img
                                src={tweet.author.profile_pic}
                                alt={tweet.author.user_name}
                                width="50"
                                height="50"
                                style={{
                                    borderRadius: '50%',
                                    marginRight: '15px',
                                }}
                            />
                            <h2 style={{
                                fontSize: '20px',
                                color: '#333',
                                margin: 0,
                            }}>
                                @{tweet.author.user_name}
                            </h2>
                        </div>
                        <p style={{
                            fontSize: '16px',
                            color: '#555',
                            margin: 0,
                            marginLeft: '15px',
                            whiteSpace: 'nowrap',
                        }}>
                            {formatFakeTime(tweet.fake_time)}
                        </p>
                    </div>
                    <div style={{
                        padding: '15px',
                        fontSize: '20px',
                        color: '#000',
                        wordBreak: 'break-word',
                    }}>
                        {tweet.text}
                    </div>
                </div>
            </div>
            ),
            {
                ...size,
                fonts: [
                    {
                        name: 'MS Sans Serif',
                        data: fontData,
                        style: 'normal',
                    },
                ],
            }
        )
    } catch (error) {
        console.error('Error generating image:', error)
        return new ImageResponse(
            (
            <div
                style={{
                width: '100%',
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: '#000000',
                color: '#c0c0c0',
                fontSize: 32,
                fontFamily: '"MS Sans Serif"',
                }}
            >
                Error loading tweet image
            </div>
            ),
            {
                ...size,
                fonts: [
                    {
                        name: 'MS Sans Serif',
                        data: fontData,
                        style: 'normal',
                    },
                ],
            }
        )
    }
}