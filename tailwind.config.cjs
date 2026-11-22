module.exports = {
  content: ['./*.html', './apps/**/*.html', './download/**/*.html', './_layouts/**/*.html', './_includes/**/*.{html,md}', './_posts/*.md', './policies/**/*.html'],
  theme: { extend: {
    fontFamily: { sans: ['Pretendard', 'system-ui', '-apple-system', 'sans-serif'] },
    colors: { cream: '#FAFAF7', sage: { DEFAULT:'#7BA886', dark:'#5A8A6A' }, ink:'#1C1C19', sub:'#6B6860', surface:'#FFFFFF' }
  } }
};
