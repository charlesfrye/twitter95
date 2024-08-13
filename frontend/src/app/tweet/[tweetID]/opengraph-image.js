import { ImageResponse } from 'next/og'
   import { baseUrl } from '../../../services/database';
    
   export const runtime = 'edge'
    
   export const alt = 'Tweet Image'
   export const size = {
     width: 800,
     height: 450,
   }
   export const contentType = 'image/png'
    
   export default async function Image({ params }) {
       const tweetID = params.tweetID;
       const imageSrc = `${baseUrl}/tweet/${tweetID}/og.jpg`
       
       try {
           const imageData = await fetch(imageSrc).then(res => res.arrayBuffer())
           
           return new ImageResponse(
               (
               <div
                   style={{
                   width: '100%',
                   height: '100%',
                   display: 'flex',
                   alignItems: 'center',
                   justifyContent: 'center',
                   backgroundColor: 'black',
                   }}
               >
                   <img src={imageData} style={{ objectFit: 'contain', width: '100%', height: '100%' }} />
               </div>
               ),
               {
                   ...size,
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
                   backgroundColor: 'white',
                   color: 'black',
                   fontSize: 32,
                   }}
               >
                   Error loading tweet image
               </div>
               ),
               {
                   ...size,
               }
           )
       }
   }