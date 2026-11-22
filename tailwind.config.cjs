module.exports = {
  content: ['./*.html', './apps/**/*.html', './download/**/*.html', './_layouts/**/*.html', './_includes/**/*.{html,md}', './_posts/*.md', './policies/**/*.html'],
  theme: { extend: {
    fontFamily: { sans: ['Pretendard', 'system-ui', '-apple-system', 'sans-serif'] },
    colors: { cream: '#FAFAF7', sage: { DEFAULT:'#7BA886', dark:'#41674C' }, ink:'#1C1C19', sub:'#615F58', surface:'#FFFFFF' }
  } }
};
