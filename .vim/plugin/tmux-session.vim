if !has('unix') || has('macunix') || exists('g:loaded_tmux_session')
  finish
endif
let g:loaded_tmux_session = 1

function! s:Save(timer) abort
  if exists('s:session_file') && get(g:, 'this_obsession', '') ==# s:session_file
    doautocmd <nomodeline> obsession BufEnter
    if filereadable(s:session_file)
      call setfperm(s:session_file, 'rw-------')
    endif
  endif
endfunction

function! s:Start() abort
  if empty($TMUX) || empty($TMUX_PANE) || !has('ttyin') || !has('ttyout')
    return
  endif
  if !exists(':Obsession')
    echoerr 'tmux session restore requires vim-obsession'
    return
  endif
  let directory = expand('~/.local/state/tmux/vim')
  call mkdir(directory, 'p', 0700)
  " A file per editor avoids collisions, even after loading the same session twice.
  let s:session_file = directory . '/' . localtime() . '-' . getpid() . '.vim'
  silent execute 'Obsession' fnameescape(s:session_file)
  call setfperm(s:session_file, 'rw-------')
  let command = shellescape(expand('~/.local/bin/tmux-app-state'))
        \ . ' vim ' . getpid() . ' ' . shellescape(s:session_file)
        \ . (&readonly ? ' --readonly' : '')
  let result = system(command)
  if v:shell_error
    echoerr 'tmux session registration failed: ' . result
    return
  endif
  " Obsession handles buffers and exit; also capture idle layout/cursor changes.
  let s:timer = timer_start(30000, function('s:Save'), {'repeat': -1})
endfunction

augroup dotfiles_linux_tmux_session
  autocmd!
  autocmd VimEnter * call s:Start()
augroup END
