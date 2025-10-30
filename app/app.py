cd frontend
npm run build
mkdir -p ../app/static
cp -r build/* ../app/static/
touch ../app/.nojekyll
git add app/
git commit -m "Deploy MVP"
git push
