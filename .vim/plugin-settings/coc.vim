if !exists('*CocAction')
    finish
endif

nnoremap <silent> C :call CocActionAsync('codeAction', '')<CR>
nnoremap <silent> K :call CocActionAsync('doHover')<CR>
nmap <silent> gd <Plug>(coc-definition)
nnoremap <silent> dz :call CocActionAsync('jumpDefinition', 'tabe')<CR>
nnoremap <silent> ds :call CocActionAsync('jumpDefinition', 'split')<CR>
nmap <silent> rr <Plug>(coc-rename)
