function! s:SessionFile() abort
    if has('macunix')
        let l:session_dir = expand('~/Library/Application Support/vim/sessions')
        call mkdir(l:session_dir, 'p', 0700)
        let l:working_dir = substitute(resolve(fnamemodify(getcwd(), ':p')), '/$', '', '')
        return l:session_dir . '/' . sha256(l:working_dir) . '.vim'
    endif

    return getcwd() . '/Session.vim'
endfunction

function! DotfilesStartTmuxSession() abort
    if empty($TMUX)
        return
    endif

    if exists('g:this_obsession') || !empty(v:this_session) || !exists(':Obsession')
        return
    endif

    let l:session = s:SessionFile()

    if filereadable(l:session) && argc() == 0
        execute 'silent source ' . fnameescape(l:session)
    else
        execute 'silent Obsession ' . fnameescape(l:session)
    endif
endfunction

augroup tmux_session
    autocmd!
    autocmd VimEnter * call DotfilesStartTmuxSession()
augroup END
