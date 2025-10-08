import json

def load_data():
  try:
    with open("youtube.txt","r") as file:
      return  json.load(file)
  except FileNotFoundError:
    return []
  
def save_video_helper(videos):
   with open("youtube.txt","w") as file:
     json.dump(videos, file)
     print("video is saved")


def list_all_videos(videos):
   
   for index,video in enumerate(videos, start=1):
     print(f"{index}.{video['video']},Duration ={video['time']}")

def Add_youtube_video(videos):
   name=input("Enter video name: ")
   time=input("Enter video time: ")
   videos.append({'video':name,'time': time})
   save_video_helper(videos)
   
def Update_video(videos):
  list_all_videos(videos)
  index=int(input("Enter a video you want to Update: "))
  if 1 <= index <= len(videos):
    name=input("Enter a Video name: ")
    time=input("Enter a video time: ")
    videos[index-1]={'video':name,'time':time}
    save_video_helper(videos)

def Delete_video(videos):
  list_all_videos(videos)
  index=int(input("Enter a video number you want to delete: "))
  if 1 <= index <= len(videos):
    deleted_video = videos.pop(index-1)
    save_video_helper(videos)
    print(f"Video '{deleted_video['video']}' has been deleted.")
  else:
    print("Invalid video number.")


def main():
    videos=load_data()
    while True:
     print("\n")
     print("1.list of youtube videos")
     print("2.Add of youtube videos")
     print("3.Update of youtube video")
     print("4.Delete a youtube video")
     print("5.exit of program")
     user_input=int(input("Choose your Option: "))
     match user_input:
      case 1:
       list_all_videos(videos)
      case 2:
       Add_youtube_video(videos)
      case 3:
       Update_video(videos)
      case 4:
       Delete_video(videos)
      case 5:
       break
       

if __name__ == "__main__":
  main()
