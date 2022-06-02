
set autoindent
"set autochdir
set autoread                    " auto refresh if file changed on disk

set backspace=2		            " Allows insert-mode backspace to work as one expects
set belloff=all

set cindent
set cinkeys=0{,0},:,!^F,o,O,e	" See "cinkeys"; this stops "#" from indenting
set cmdheight=2                 " Give more space for displaying messages.

set encoding=utf-8
set expandtab

set fileformat=unix	            " No crazy CR/LF

set gdefault                    " gdefault applies substitutions globally on lines: instead of :%s/foo/bar/g, just type :%s/foo/bar/

set hidden
set hlsearch                    " highlight search terms:  search smartly.. and easily: http://stevelosh.com/blog/2010/09/coming-home-to-vim/

set ignorecase                  " search intelligently : http://stevelosh.com/blog/2010/09/coming-home-to-vim/
set incsearch                   " show search matches as you type

set listchars=tab:\ \ ,trail:·  " If you do ":set list", shows trailing spaces

set nobackup
set nobackup		            " Don't use a backup file (also see writebackup)
set nocompatible
set nojoinspaces	            " One space after a "." rather than 2
set noswapfile
set nu


set scrolloff=1		            " Minimum lines between cursor and window edge
set shiftwidth=4	            " Indent by 4 columns (for C functions, etc).
set showcmd		                " Show partially typed commands
set showmatch		            " Show parentheses matching
set signcolumn=yes              " used by language server client
set smartcase                   " search intelligently : http://stevelosh.com/blog/2010/09/coming-home-to-vim/
set smartindent		            " Indent settings (really only the cindent matters)
set softtabstop=4 

set ruler		                " Show the line position at the bottom of the window
set relativenumber

set tabstop=4 
set textwidth=180	            " Maximum line width

set updatetime=50               " longer updatetime (default: 4000ms) leads to noticeable delays and poor user experience.
set undodir=~/.vim/undodir      " used by plugin: undotree
set undofile                    " used by plugin: undotree


set wildignore=*.swp,*.bak,*.*.pyc,*.class,*/.git/**/* 
set wildignorecase
set wildmenu                    " shows a list of matching files when tab completing in command mode, like with :tabe
set wildmode=list:full          " https://www.reddit.com/r/vim/comments/1p2a62/a_painless_tutorial_on_vim_buffers/ccxzq7e/
set whichwrap=<,>,[,],h,l       " Allows for left/right keys to wrap across lines
set writebackup		            " Write temporary backup files in case we crash

"set viminfo='0,\"100,	        " Stay at the start of a file when opening it
"
set shortmess-=S                " Show number of matching on ? /

set matchpairs+=<:>

" Use `[c` and `]c` to navigate diagnostics
nmap <silent> [c <Plug>(coc-diagnostic-prev)
nmap <silent> ]c <Plug>(coc-diagnostic-next)

" Remap keys for gotos
"nmap <silent> gd <Plug>(coc-definition)
"nmap <silent> gy <Plug>(coc-type-definition)
"nmap <silent> gi <Plug>(coc-implementation)
"nmap <silent> gr <Plug>(coc-references)

" Use K to show documentation in preview window
"nnoremap <silent> K :call <SID>show_documentation()<CR>
"nmap <silent>K <Plug>(lcn-hover)

function! s:show_documentation()
  if (index(['vim','help'], &filetype) >= 0)
    execute 'h '.expand('<cword>')
  else
    call CocAction('doHover')
  endif
endfunction

" Highlight symbol under cursor on CursorHold
autocmd CursorHold * silent call CocActionAsync('highlight')

" Remap for rename current word
nmap <leader>rn <Plug>(coc-rename)

" Remap for format selected region
xmap <leader>f  <Plug>(coc-format-selected)
nmap <leader>f  <Plug>(coc-format-selected)

augroup mygroup
  autocmd!
  " Setup formatexpr specified filetype(s).
  autocmd FileType typescript,json setl formatexpr=CocAction('formatSelected')
  " Update signature help on jump placeholder
  autocmd User CocJumpPlaceholder call CocActionAsync('showSignatureHelp')
augroup end

" Remap for do codeAction of selected region, ex: `<leader>aap` for current paragraph
xmap <leader>a  <Plug>(coc-codeaction-selected)
nmap <leader>a  <Plug>(coc-codeaction-selected)

" Remap for do codeAction of current line
nmap <leader>ac  <Plug>(coc-codeaction)
" Fix autofix problem of current line
nmap <leader>qf  <Plug>(coc-fix-current)

" Use <tab> for select selections ranges, needs server support, like: coc-tsserver, coc-python
nmap <silent> <TAB> <Plug>(coc-range-select)
xmap <silent> <TAB> <Plug>(coc-range-select)
xmap <silent> <S-TAB> <Plug>(coc-range-select-backword)

" Use `:Format` to format current buffer
command! -nargs=0 Format :call CocAction('format')

" Use `:Fold` to fold current buffer
command! -nargs=? Fold :call     CocAction('fold', <f-args>)

" use `:OR` for organize import of current buffer
command! -nargs=0 OR   :call     CocAction('runCommand', 'editor.action.organizeImport')

" Add status line support, for integration with other plugin, checkout `:h coc-status`
set statusline^=%{coc#status()}%{get(b:,'coc_current_function','')}

" Using CocList
" Show all diagnostics
nnoremap <silent> <space>a  :<C-u>CocList diagnostics<cr>
" Manage extensions
nnoremap <silent> <space>e  :<C-u>CocList extensions<cr>
" Show commands
nnoremap <silent> <space>c  :<C-u>CocList commands<cr>
" Find symbol of current document
nnoremap <silent> <space>o  :<C-u>CocList outline<cr>
" Search workspace symbols
nnoremap <silent> <space>s  :<C-u>CocList -I symbols<cr>
" Do default action for next item.
nnoremap <silent> <space>j  :<C-u>CocNext<CR>
" Do default action for previous item.
nnoremap <silent> <space>k  :<C-u>CocPrev<CR>
" Resume latest coc list
nnoremap <silent> <space>p  :<C-u>CocListResume<CR>
