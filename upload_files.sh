for file in /Users/danielsamuels/Documents/Clients/Personal\ Projects/Rocket\ League\ Replays/Demos/*
do
  echo $file
  curl -X POST -H "Content-Type: multipart/form-data" -F "file=@$file" 'http://127.0.0.1:8000/api/replays/' >/dev/null 2>&1
done
