import streamlit as st
import yt_dlp
import os
import base64
import subprocess
import requests
from io import BytesIO
from moviepy import VideoFileClip

class YouTubeDownloader:
    @staticmethod
    def download_video(url, output_path, resolution='best'):
        """
        Download YouTube video with advanced options
        """
        try:
            os.makedirs(output_path, exist_ok=True)
            
            if resolution == 'best':
                format_spec = 'bestvideo+bestaudio/best'
            else:
                format_spec = f'bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]'
            
            ydl_opts = {
                'format': format_spec,
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'merge_output_format': 'mp4'
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_title = info.get('title', 'unknown')
                filename = ydl.prepare_filename(info)
            
            return filename
        
        except Exception as e:
            st.error(f"Download error: {e}")
            return None

    @staticmethod
    def crop_video(input_file, start_time, end_time, output_path):
        """
        Crop video to specified time range
        """
        try:
            subprocess.run([
                'ffmpeg', 
                '-i', input_file,
                '-ss', start_time,
                '-to', end_time,
                '-c:v', 'libx264',  # Use H.264 encoding for compatibility
                '-preset', 'fast',
                '-crf', '23',  # Controls video quality (lower = better)
                '-c:a', 'aac',  # Ensure proper audio encoding
                '-b:a', '192k',
                #'-c', 'copy',
                output_path
            ], check=True)
            
            return output_path
        
        except Exception as e:
            st.error(f"Crop error: {e}")
            return None

    @staticmethod
    def extract_audio(input_file, output_path):
        """
        Extract audio from video
        """
        try:
            if not os.path.exists(input_file):
                st.error(f"Input file not found: {input_file}")
                return None
                
            video = VideoFileClip(input_file)
            if video.audio is None:
                st.error("No audio stream found in video")
                return None
                
            video.audio.write_audiofile(output_path)
            video.close()
            
            if os.path.exists(output_path):
                return output_path
            else:
                st.error("Failed to create audio file")
                return None
                
        except Exception as e:
            st.error(f"Audio extraction error: {e}")
            return None
        
def set_background(image_path):
    try:

        response=requests.get(image_path)
        if response.status_code == 200:
            encoded_string = base64.b64encode(BytesIO(response.content).read()).decode()
    
    
    
        #"""if not os.path.exists(image_path):
        #    st.error(f"Image file not found: {image_path}")
        #    return
        #
        #with open(image_path, "rb") as img_file:
        #    encoded_string = base64.b64encode(img_file.read()).decode()"""
    
            page_bg_img = f"""
            <style>
        
            @import url('https://fonts.googleapis.com/css2?family=Pacifico&family=Tomorrow:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');
            html, body, [class*="stTitle"] {{
                font-family: 'Pacifico', cursive;
            
            }}
            h1,h2,h3,h4,h5,h6 {{
                font-family: 'Pacifico', cursive;
                text-align: center;
                text-shadow: -4px -4px 0 black,  
                          4px -4px 0 black,  
                         -4px  4px 0 black,  
                          4px  4px 0 black;
            }}
            p, label,div, span{{
                font-family: 'Pacifico', cursive;
                font-size: 1rem !important;  /* Increase size */
                text-shadow: -2px -2px 0 black,  
                          2px -2px 0 black,  
                         -2px  2px 0 black,  
                          2px  2px 0 black;
            }}
        
            [data-testid="stMarkdownContainer"] h1 {{
            font-family: 'Pacifico', cursive !important;
            font-size: 4.5rem !important;  /* Increase size */
            text-align: center;
            color: white;
            text-shadow: -4px -4px 0 black,  
                          4px -4px 0 black,  
                         -4px  4px 0 black,  
                          4px  4px 0 black; /* Stronger outline for title */
            }}
            
        
            [data-testid="stAppViewContainer"] {{
                background-image: url("data:image/jpg;base64,{encoded_string}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
            }}
            [data-testid="stHeader"] {{
                background: rgba(0,0,0,0);
            }}
        
            [data-testid="stSidebar"] {{
            background: rgba(255, 255, 255, 0.1); /* Light transparent background */
            backdrop-filter: blur(10px); /* Blur effect for glassmorphism */
            -webkit-backdrop-filter: blur(10px); /* For Safari support */
            border-radius: 10px; /* Slight rounded edges */
            padding: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2); /* Subtle shadow for depth */
            }}
        
            
            </style>
            """
            st.markdown(page_bg_img, unsafe_allow_html=True)
        else:
            st.warning("Image not found")
    

    except Exception as e:
        st.warning(f"Error setting background: {e}")

def main():
    image_path = "https://raw.githubusercontent.com/srinivassake/you-downloader/refs/heads/main/background.png"
    set_background(image_path)
    st.title("YouDownloader !")
    
    st.sidebar.header("Download Options")
    download_option = st.sidebar.selectbox(
        "Choose Download Type", 
        ["Full Video", "Crop Video", "Audio Only"]
    )
    
    video_url = st.text_input("Enter YouTube Video URL")
    download_path = st.text_input("Download Path", value="downloads")
    
    if download_option == "Crop Video":
        col1, col2 = st.columns(2)
        with col1:
            start_time = st.text_input("Start Time (HH:MM:SS)", value="00:00:00")
        with col2:
            end_time = st.text_input("End Time (HH:MM:SS)", value="00:01:00")
    
    if download_option == "Full Video":
        resolution = st.sidebar.selectbox(
            "Select Resolution", 
            ["best", "1080p", "720p", "480p", "360p"]
        )
    else:
        resolution = "best"
    
    if st.button("Download"):
        if video_url:
            with st.spinner('Processing...'):
                if download_option == "Full Video":
                    video_file = YouTubeDownloader.download_video(
                        video_url, 
                        download_path, 
                        resolution
                    )
                    if video_file:
                        st.success(f"Video downloaded: {video_file}")
                
                elif download_option == "Crop Video":
                    video_file = YouTubeDownloader.download_video(
                        video_url, 
                        download_path
                    )
                    #"""if video_file:
                    #    cropped_video = os.path.join(
                    #        download_path, 
                    #        f"cropped_{os.path.basename(video_file)}"
                    #    )
                    #    result = YouTubeDownloader.crop_video(
                    #        video_file, 
                    #        start_time, 
                    #        end_time, 
                    #        cropped_video
                    #    )
                    #    if result:
                    #        st.success(f"Video cropped: {result}")"""
                    if video_file:
                        cropped_video = os.path.join(
                            download_path, 
                            f"cropped_{os.path.basename(video_file)}"
                        )
                        result = YouTubeDownloader.crop_video(
                            video_file, 
                            start_time, 
                            end_time, 
                            cropped_video
                        )
                        if result:
                            st.success(f"Video cropped: {result}")
                            try:
                                os.remove(video_file)  # Remove full video after cropping
                            except Exception as e:
                                st.warning(f"Could not delete full video: {e}")
        
                
                elif download_option == "Audio Only":
                    video_file = YouTubeDownloader.download_video(
                        video_url, 
                        download_path
                    )
                    if video_file:
                        audio_file = os.path.join(
                            download_path, 
                            f"audio_{os.path.splitext(os.path.basename(video_file))[0]}.mp3"
                        )
                        result = YouTubeDownloader.extract_audio(
                            video_file, 
                            audio_file
                        )
                        if result:
                            st.success(f"Audio extracted: {result}")
                            try:
                                os.remove(video_file)  # Clean up video file
                            except:
                                pass
        else:
            st.warning("Please enter a YouTube URL")

if __name__ == "__main__":
    main()