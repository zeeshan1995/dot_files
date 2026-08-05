syntax enable
filetype plugin indent on

let mapleader = ' '

if has('macunix')
    let g:coc_data_home = expand('~/Library/Application Support/coc')
endif

source ~/.vim/set-cmds.vim
source ~/.vim/plugins.vim

source ~/.vim/plugin-settings/fzf.vim
source ~/.vim/plugin-settings/coc.vim
source ~/.vim/plugin-settings/lightline.vim
source ~/.vim/plugin-settings/nerdtree.vim
source ~/.vim/plugin-settings/undotree.vim
source ~/.vim/plugin-settings/vim-sneak.vim
source ~/.vim/mappings.vim

let g:rg_command = 'rg --vimgrep --smart-case'

if !empty(globpath(&runtimepath, 'colors/molokai.vim'))
    colorscheme molokai
endif

highlight LineNr term=bold cterm=NONE ctermfg=DarkGrey ctermbg=233

command! FormatJson %!python3 -m json.tool

augroup dotfiles
    autocmd!
    autocmd BufReadPost * if line("'\"") > 1 && line("'\"") <= line("$") | execute "normal! g'\"" | endif
augroup END
