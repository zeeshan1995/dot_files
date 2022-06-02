
syntax on
filetype plugin on

let mapleader=' '

source ~/.vim/set-cmds.vim

source ~/.vim/plugins.vim

source ~/.vim/plugin-settings/fzf.vim
source ~/.vim/plugin-settings/language-client.vim
source ~/.vim/plugin-settings/lightline.vim
source ~/.vim/plugin-settings/nerdtree.vim
source ~/.vim/plugin-settings/undotree.vim
source ~/.vim/plugin-settings/vim-sneak.vim

source ~/.vim/mappings.vim

let g:rg_command = 'rg --vimgrep'
colorscheme molokai

" have vim jump to the last position when reopening a file
au BufReadPost * if line("'\"") > 1 && line("'\"") <= line("$") | exe "normal! g'\"" | endif

"http://stackoverflow.com/questions/4206360/vim-how-to-change-font-color-of-current-line-number
highlight LineNr term=bold cterm=NONE ctermfg=DarkGrey ctermbg=233

" format json file 
" https://stackoverflow.com/questions/26214156/how-to-auto-format-json-on-save-in-vim
com! FormatJson %!python -m json.tool

" https://github.com/vim/vim/issues/704
"autocmd VimEnter * set autochdir

"autocmd StdinReadPre * let s:std_in=1
"autocmd VimEnter * if argc() == 0 && !exists("s:std_in") | NERDTree | endif
