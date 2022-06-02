
" LANGUAGE SERVER
"
" > https://langserver.org/
" > https://github.com/autozimu/LanguageClient-neovim/blob/next/INSTALL.md
" > https://github.com/theia-ide/typescript-language-server

let g:LanguageClient_serverCommands = {
    \ 'rust': ['~/.cargo/bin/rustup', 'run', 'stable', 'rls'],
    \ 'javascript': ['/usr/local/bin/javascript-typescript-stdio'],
    \ 'javascript.jsx': ['tcp://127.0.0.1:2089'],
    \ 'python': ['/usr/local/bin/pyls'],
    \ 'ruby': ['~/.rbenv/shims/solargraph', 'stdio'],
    \ 'cpp': ['/usr/bin/clangd', '--enable-config', '--all-scopes-completion', '--background-index'],
    \ }

nnoremap C :call LanguageClient_contextMenu()<CR>
"nnoremap <silent> K :call LanguageClient#textDocument_hover()<CR>
nmap <silent> K :call LanguageClient#textDocument_hover()<CR>
nnoremap <silent> gd :call LanguageClient#textDocument_definition()<CR>
nnoremap <silent> dg :tab :call LanguageClient#textDocument_definition()<CR>
nnoremap <silent> ds :vsp :call LanguageClient#textDocument_definition()<CR>
nnoremap <silent> rr :call LanguageClient#textDocument_rename()<CR>

