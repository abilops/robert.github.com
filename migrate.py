import os

posts_dir = "./_posts"

for fname in os.listdir(posts_dir):
    path = os.path.join(posts_dir, fname)

    bits = fname.split("-", 3)
    url = f"/{bits[0]}/{bits[1]}/{bits[2]}/{bits[3].rstrip('.md')}"
    print(url)

    with open(path, 'w') as f:
        ls = f.readlines()
        ls.insert(1, f"permalink: {url}")
        f.writelines(ls)
