Vendor Performance Analysis Data Analytics Project




---

### ✅ First Time Upload with Git LFS (Initial Setup)

```bash
git init
git lfs install
git lfs track "*.csv" "*.pkl" "*.h5" "*.zip" "*.pt"
git add .gitattributes
git add .
git commit -m "Initial commit with LFS"
git remote remove origin 2>/dev/null
git remote add origin https://github.com/your-username/your-repo.git
git branch -M main
git push -u origin main --force
```

> 🔁 Replace `your-username/your-repo.git` with your actual GitHub repo URL.

---

### 🔄 Upload New Files or Updates Later

Whenever you add or update files, use:

```bash
git checkout main   # Stay on main branch
git pull origin main --rebase
git status          # Optional: show status before commit
git add .
git commit -m "Updated project files" || echo \"Nothing to commit\"
git push origin main
```

---

### ➕ If You Add a New Large File Type (Optional)

```bash
git lfs track "*.new_ext"
git add .gitattributes
git add .
git commit -m "Track new file type"
git push origin main
```

---

NOT ABLE TO MAKE POWER BI DASHBOARD DUE TO SORTAGE OF RESOURCES. 
