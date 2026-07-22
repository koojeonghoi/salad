
export const STORES=[
{id:"prep",name:"프레퍼스",menus:[
{id:"pcp",name:"치킨 샐러드 파스타",price:8900,kcal:411,protein:43,ing:["chicken","pasta"]},
{id:"ppp",name:"포크 샐러드 파스타",price:8900,kcal:437,protein:44,ing:["pork","pasta"]},
{id:"pbp",name:"비프 샐러드 파스타",price:13900,kcal:578,protein:50,ing:["beef","pasta"]},
{id:"pdt",name:"치킨 데리야끼 덮밥",price:9900,kcal:492,protein:44,ing:["chicken","grain"]},
{id:"pcc",name:"치킨 커리 덮밥",price:9900,kcal:591,protein:44,ing:["chicken","grain"]},
{id:"ppc",name:"포크 커리 덮밥",price:10900,kcal:622,protein:45,ing:["pork","grain"]},
{id:"pbc",name:"비프 커리 덮밥",price:13900,kcal:731,protein:51,ing:["beef","grain"]}]},
{id:"salady",name:"샐러디",menus:[
{id:"sr",name:"로스트닭다리살 샐러디",price:12000,kcal:259,protein:13.2,ing:["chicken"]},
{id:"ss",name:"그라브락스 연어 샐러디",price:13700,kcal:247,protein:21,ing:["salmon"]},
{id:"sb",name:"우삼겹메밀면 누들볼",price:10700,kcal:407,protein:18,ing:["beef","buckwheat"]}]},
{id:"poke",name:"포케올데이",menus:[
{id:"pt",name:"곡물밥 스파이시 참치 포케",price:12900,kcal:623,protein:33.5,ing:["tuna","grain","spicy"]},
{id:"pd",name:"곡물밥 훈제오리 포케",price:11900,kcal:732,protein:25.2,ing:["grain"]}]},
{id:"slow",name:"슬로우캘리",menus:[{id:"sl",name:"클래식 연어 포케",price:12500,kcal:569,protein:30,ing:["salmon","grain","seaweed"]}]},
{id:"subway",name:"써브웨이",menus:[
{id:"se",name:"에그마요 15cm",price:6200,kcal:453,protein:16.9,ing:["egg","mayo"]},
{id:"src",name:"로티세리 바비큐 치킨 15cm",price:7800,kcal:328,protein:29.1,ing:["chicken"]},
{id:"ssh",name:"쉬림프 15cm",price:8200,kcal:281,protein:16.3,ing:["shrimp"]}]}
];
export const TARGET={diet:{name:"다이어트",min:250,max:450,p:18},protein:{name:"고단백",min:300,max:700,p:30},light:{name:"가볍게",min:200,max:400,p:12},filling:{name:"든든하게",min:500,max:800,p:25},balanced:{name:"균형 있게",min:350,max:650,p:20},any:{name:"아무거나",min:0,max:9999,p:0}};
