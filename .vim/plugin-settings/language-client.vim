
" LANGUAGE SERVER
"
" > https://langserver.org/
" > https://github.com/autozimu/LanguageClient-neovim/blob/next/INSTALL.md
" > https://github.com/theia-ide/typescript-language-server

let g:LanguageClient_serverCommands = {
    \ 'rust': ['~/.cargo/bin/rustup', 'run', 'stable', 'rls'],
    \ 'javascript': ['/usr/local/bin/javascript-typescript-stdio'],
    \ 'javascript.jsx': ['tcp://127.0.0.1:2089'],
    \ 'python': ['/usr/local/bin/pylsp'],
    \ 'ruby': ['~/.rbenv/shims/solargraph', 'stdio'],
    \ 'cpp': ['/usr/bin/clangd-12', '--enable-config', '--all-scopes-completion', '--background-index'],
    \ }

nnoremap C :call LanguageClient_contextMenu()<CR>
"nnoremap <silent> K :call LanguageClient#textDocument_hover()<CR>
nmap <silent> K :call LanguageClient#textDocument_hover()<CR>
nnoremap <silent> gd :call LanguageClient#textDocument_definition()<CR>
" https://github.com/autozimu/LanguageClient-neovim/issues/395#issuecomment-383655421
nnoremap <silent> dz :call LanguageClient#textDocument_definition({'gotoCmd': 'tabedit'})<CR>
nnoremap <silent> ds :call LanguageClient#textDocument_definition({'gotoCmd': 'split'})<CR>
nnoremap <silent> rr :call LanguageClient#textDocument_rename()<CR>

