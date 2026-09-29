set nocompatible
set nomore
source ~/.vim/plugins.vim
PlugInstall --sync
if !empty(filter(getline(1, '$'), 'v:val =~# "^x "'))
  call writefile(getline(1, '$'), '/dev/stderr')
  cquit 1
endif
PlugStatus
if getline(1) !=# 'Finished. 0 error(s).'
  call writefile(getline(1, '$'), '/dev/stderr')
  cquit 1
endif
qa!
