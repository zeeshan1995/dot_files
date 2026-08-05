set nocompatible
set encoding=utf-8
set fileformat=unix

set autoindent
set autoread
set backspace=indent,eol,start
set belloff=all
set cindent
set cinkeys=0{,0},:,!^F,o,O,e
set expandtab
set shiftwidth=4
set smartindent
set softtabstop=4
set tabstop=4
set textwidth=180

set gdefault
set hidden
set ignorecase
set incsearch
set hlsearch
set smartcase

set number
set relativenumber
set ruler
set scrolloff=3
set showcmd
set showmatch
set signcolumn=yes

set listchars=tab:\ \ ,trail:·
set matchpairs+=<:>
set nojoinspaces
set shortmess-=S
set splitbelow
set splitright
set updatetime=300
set whichwrap=<,>,[,],h,l

set completeopt=menuone,noselect
set wildignore=*.swp,*.bak,*.*.pyc,*.class,*/.git/**/*
set wildignorecase
set wildmenu
set wildmode=list:full
if exists('+wildoptions')
    set wildoptions=pum
endif

if has('termguicolors')
    set termguicolors
endif

if has('macunix')
    let s:vim_cache = expand('~/Library/Caches/vim')
else
    let s:vim_cache = expand('~/.cache/vim')
endif

execute 'set backupdir=' . fnameescape(s:vim_cache . '/backup//')
execute 'set directory=' . fnameescape(s:vim_cache . '/swap//')
execute 'set undodir=' . fnameescape(s:vim_cache . '/undo//')
set backup
set swapfile
set undofile
set writebackup

if executable('rg')
    set grepprg=rg\ --vimgrep\ --smart-case
    set grepformat=%f:%l:%c:%m
endif

unlet s:vim_cache
