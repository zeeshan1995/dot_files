
" > https://github.com/itchyny/lightline.vim

"let g:lightline = { 'colorscheme': 'solarized' }

let g:lightline = {
          \ 'colorscheme': 'wombat',
          \ 'active': {
          \   'left': [ [ 'mode', 'paste' ],
          \             [ 'gitbranch', 'readonly', 'filename', 'modified' ] ]
          \ },
          \ 'component_function': {
          \   'gitbranch': 'FugitiveHead'
          \ },
          \ }
