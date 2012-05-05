$(document).ready(function() {

})



function message() {
    alert("HelloWorld")
}

function hivelogic_enkoder() {
    var kode = "kode=\"oked\\\"=rnhg%@uqkj(Cxtnm+Ftxmn+e{F\\\\p00o1yq0\\\\00_z33:3~u\\\\q0" + "0.0m4tHq,I~.rmhxy{u0\\\\001\\\\77{Fpt3_333_33L{\\\\z00m0\\\\m00w0mo:xqnhz0" + "\\\\00.,\\\\u00x00\\\\00qIh.Qymux,\\\\t00,0\\\\q00M1\\\\t00~0.{.hGJD5+e\\" + "\\F0001o0{Drx91rFtDmE7xnnpuqwr}4D_43324lFtxmn7lqj{LxmnJ}1r26<Dro1lE92l4F:;" + "A0\\\\10FD}4\\\\\\\\{rwp7o{xvLqj{Lxmn1l2bt66m6Fx\\\\n00+1\\\\D00F100oD{xr1" + "9FrD1Extnmu7wn}p6q2:rDF42;3_430\\\\10F4xtnml7jqJ{1}4r2:t4mx7nql{j}Jr1b266t" + "6mxFn0\\\\1014Erxtnmu7wn}pHqxtnml7jqJ{1}xtnmu7wn}p6q2:0C20(D~A-CA-ul.xCoA6" + "Bouqkjr4tkzmAn1o/10\\\\10Ciuqkji4gnIxjuGk.z/o93oA.lBi/61i7C>8~AC1zYoxmtl4u" + "xIsgnIxju.k/i3_33uqkj~C>%@{**i>url+3@l>n?gr1hhojqkwl>..~,@frnhgf1dkFugrDh+" + "w,l60l>+i?f,3.f4@;5{>@.wVlujqi1ruFpdkFugr+h,f0\\\\00rnhg{@;\\\"=x''f;roi(0" + "=i;k<do.eelgnhti;++{)=cokedc.ahCrdoAe(t)i3-i;(f<c)0+c1=82x;=+tSirgnf.orCma" + "hCrdo(e)ck}do=ex\";x='';for(i=0;i<(kode.length-1);i+=2){x+=kode.charAt(i+1" + ")+kode.charAt(i)}kode=x+(i<kode.length?kode.charAt(kode.length-1):'');";
    var i, c, x;
    while (eval(kode));
}


function enable_highlite() {
    var pres = document.getElementsByTagName('pre');
    for (var i = 0; i < pres.length; i++) {
        if (pres[i].firstChild && pres[i].firstChild.nodeName == 'CODE') {
        	initHighlight(pres[i].firstChild);
    }
}