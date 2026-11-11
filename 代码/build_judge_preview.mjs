import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const out=path.join(root,'03_Judge一致性标注','模拟预览_非真实实验');
const auxiliary=path.join(out,'辅助文件');
await fs.mkdir(auxiliary,{recursive:true});
const data=JSON.parse(await fs.readFile(path.join(auxiliary,'模拟统计.json'),'utf8'));
const wb=Workbook.create();
const s=wb.worksheets.add('模拟结果_非真实实验');
const d=wb.worksheets.add('模拟标签_非人工标注');
const base={font:{name:'Arial',size:11,color:'#1F2937'},rowHeight:24,verticalAlignment:'center'};
for(const sh of [s,d]){sh.showGridLines=false;sh.tabColor='#994D00';}
s.getRange('A1:I76').format=base;
s.getRange('A1:A76').format.columnWidth=37;
s.getRange('B1:I76').format.columnWidth=16;
d.getRange('A1:J2003').format=base;
d.getRange('A1:A2003').format.columnWidth=15;
d.getRange('B1:B2003').format.columnWidth=37;
d.getRange('C1:D2003').format.columnWidth=22;
d.getRange('E1:J2003').format.columnWidth=17;
d.freezePanes.freezeRows(3);
function title(sh,cell,text){sh.getRange(cell).values=[[text]];sh.getRange(cell).format.font={name:'Arial',size:16,bold:true,color:'#994D00'};}
function header(sh,range,values){sh.getRange(range).values=[values];sh.getRange(range).format={fill:'#35445B',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},rowHeight:30,horizontalAlignment:'center'};}
title(s,'A2','一致性模拟预览（非真实实验）');
s.getRange('A3').values=[['A/B由程序生成；真实专家均未标注。ρ按11个模型排名计算，κ按2,000条标签计算。']];
s.getRange('A4').values=[['按目标范围筛选的模拟值，仅用于查看效果，不能用于验证Judge可靠性。']];
s.getRange('A3:A4').format.font={name:'Arial',size:11,color:'#994D00'};
header(s,'A6:E6',['模拟比较','一致率','Cohen’s κ','Spearman ρ','Kendall τ-b']);
const cols=[['H','I'],['H','J'],['I','J']];
const rankCols=[['F','G'],['F','H'],['G','H']];
for(let i=0;i<3;i++){
  const r=7+i, c=31+i;
  s.getRange(`A${r}:E${r}`).values=[[data.metrics[i].pair,null,null,null,data.metrics[i].kendall_model]];
  s.getRange(`B${r}:D${r}`).formulas=[[`=G${c}`,`=I${c}`,`=CORREL(${rankCols[i][0]}15:${rankCols[i][0]}25,${rankCols[i][1]}15:${rankCols[i][1]}25)`]];
}
s.getRange('B7:B9').setNumberFormat('0.00%');
s.getRange('C7:E9').setNumberFormat('0.000');
s.getRange('A11').values=[['Judge列取自现有抽样记录；A/B列为模拟。该表不是已完成的专家实验。']];
title(s,'A13','模拟模型准确率与排名');
header(s,'A14:H14',['模型','样本数','模拟A','模拟B','现有Judge','A排名','B排名','Judge排名']);
const dr="'模拟标签_非人工标注'";
for(let i=0;i<11;i++){
  const r=15+i;
  s.getRange(`A${r}`).values=[[data.models[i].model]];
  s.getRange(`B${r}:E${r}`).formulas=[[
    `=COUNTIFS(${dr}!$B$4:$B$2003,A${r})`,
    ...['H','I','J'].map(c=>`=SUMIFS(${dr}!$${c}$4:$${c}$2003,${dr}!$B$4:$B$2003,A${r})/B${r}`)
  ]];
  s.getRange(`F${r}:H${r}`).formulas=[['C','D','E'].map(c=>`=COUNTIFS($${c}$15:$${c}$25,">"&${c}${r})+(COUNTIFS($${c}$15:$${c}$25,${c}${r})+1)/2`)];
}
s.getRange('B15:B25').setNumberFormat('0');
s.getRange('C15:E25').setNumberFormat('0.00%');
s.getRange('F15:H25').setNumberFormat('0.0');
s.getRange('A26').values=[['合计']];s.getRange('B26').formulas=[['=SUM(B15:B25)']];
s.getRange('A26:H26').format.borders={top:{style:'thin',color:'#B8C2CC'}};
title(s,'A29','模拟κ计算过程（二分类）');
header(s,'A30:I30',['模拟比较','均正确','前正确后错','前错后正确','均不正确','条数','实际一致率','偶然一致率','Cohen’s κ']);
for(let i=0;i<3;i++){
  const r=31+i,[a,b]=cols[i];
  s.getRange(`A${r}`).values=[[data.metrics[i].pair]];
  s.getRange(`B${r}:E${r}`).formulas=[[[1,1],[1,0],[0,1],[0,0]].map(([x,y])=>`=COUNTIFS(${dr}!$${a}$4:$${a}$2003,${x},${dr}!$${b}$4:$${b}$2003,${y})`)];
  s.getRange(`F${r}:I${r}`).formulas=[[
    `=SUM(B${r}:E${r})`,`=(B${r}+E${r})/F${r}`,
    `=((B${r}+C${r})*(B${r}+D${r})+(D${r}+E${r})*(C${r}+E${r}))/F${r}^2`,
    `=IF(H${r}=1,"n.a.",(G${r}-H${r})/(1-H${r}))`
  ]];
}
s.getRange('G31:H33').setNumberFormat('0.00%');s.getRange('I31:I33').setNumberFormat('0.000');
title(s,'A36','模拟三分类补充');
header(s,'A37:D37',['模拟比较','普通κ','线性加权κ','题目级Spearman']);
s.getRange('A38:D40').values=data.metrics.map(r=>[r.pair,r.kappa3,r.weighted_kappa3,r.spearman_item]);
s.getRange('B38:D40').setNumberFormat('0.000');
s.getRange('A42').values=[['三分类编码：错误=0，部分正确=1，正确=2。题目级ρ与11模型排名ρ是不同指标。']];
function kappa(rows,a,b){let n=rows.length,po=rows.filter(r=>r[a]===r[b]).length/n,pa=rows.reduce((v,r)=>v+r[a],0)/n,pb=rows.reduce((v,r)=>v+r[b],0)/n,pe=pa*pb+(1-pa)*(1-pb);return pe===1?'n.a.':(po-pe)/(1-pe);}
const binaries=['模拟A二分类','模拟B二分类','现有Judge二分类'];
function breakdown(field,row){
  const groups=[...new Set(data.rows.map(r=>r[field]))].sort();
  header(s,`A${row}:E${row}`,[field,'条数','模拟A–B κ','模拟A–Judge κ','模拟B–Judge κ']);
  for(let i=0;i<groups.length;i++){
    const rows=data.rows.filter(r=>r[field]===groups[i]);
    s.getRange(`A${row+1+i}:E${row+1+i}`).values=[[groups[i],rows.length,kappa(rows,binaries[0],binaries[1]),kappa(rows,binaries[0],binaries[2]),kappa(rows,binaries[1],binaries[2])]];
  }
  s.getRange(`C${row+1}:E${row+groups.length}`).setNumberFormat('0.000');
  s.getRange(`C${row+1}:E${row+groups.length}`).format.horizontalAlignment='right';
}
title(s,'A45','模拟结果按任务分组');breakdown('任务',46);
title(s,'A53','模拟结果按学科分组');breakdown('学科',54);
s.getRange('A66').values=[['模拟生成：固定Judge标签，加相关随机扰动；三组模型排名ρ被筛选至0.85–0.95。']];
s.getRange('A67').values=[[`随机种子：${data.seed}；选中候选：${data.selected_attempt}。模拟κ点估计接近不等于实际人类一致性。`]];
s.getRange('A68').values=[['主表准确率、排名和二分类κ为公式；τ、三分类和分组κ由同一模拟标签计算并保存为快照。']];
s.getRange('A69').values=[['此文件用于固定模拟场景展示；改动标签后，补充统计需重新运行生成脚本。']];
title(d,'A1','模拟标签（A/B非人工标注）');
d.getRange('A2').values=[['来源：判定答案键_勿外发.csv；Judge沿用原值；A/B为目标筛选模拟。0=错误，1=部分正确，2=正确。']];
header(d,'A3:J3',['模拟编号','模型','任务','学科','模拟A三分类','模拟B三分类','Judge三分类','模拟A二分类','模拟B二分类','Judge二分类']);
const label={'错误':0,'部分正确':1,'正确':2};
d.getRange('A4:J2003').values=data.rows.map(r=>[r['模拟编号'],r['模型'],r['任务'],r['学科'],label[r['模拟A']],label[r['模拟B']],label[r['现有Judge']],r[binaries[0]],r[binaries[1]],r[binaries[2]]]);
d.getRange('E4:F2003').format.fill='#FFF3D6';
d.tables.add('A3:J2003',true,'SimulatedLabels');
wb.recalculate();
const actual=s.getRange('B7:D9').values;
for(let i=0;i<3;i++){
  const expected=[data.metrics[i].agreement,data.metrics[i].kappa,data.metrics[i].spearman_model];
  for(let j=0;j<3;j++)if(Math.abs(actual[i][j]-expected[j])>1e-10 || typeof actual[i][j]!=='number')throw new Error(`metric mismatch ${i},${j}: ${actual[i][j]} vs ${expected[j]}`);
}
console.log(JSON.stringify({checkedMetrics:actual,total:s.getRange('B26').values}));
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!',options:{useRegex:true,maxResults:20},summary:'formula checks'})).ndjson);
for(const [name,sh,range] of [['summary',s,'A1:H26'],['calculations',s,'A29:I42'],['breakdown',s,'A45:F69'],['data',d,'A1:J10']]){
  const preview=await wb.render({sheetName:sh.name,range,scale:1.4,format:'png'});
  await fs.writeFile(path.join(auxiliary,`preview_${name}.png`),new Uint8Array(await preview.arrayBuffer()));
}
const file=await SpreadsheetFile.exportXlsx(wb);
await file.save(path.join(out,'模拟一致性预览_非真实实验.xlsx'));
const inspection=path.join(out,'模拟一致性预览_非真实实验.xlsx.inspect.ndjson');
try{await fs.rename(inspection,path.join(auxiliary,path.basename(inspection)));}
catch(error){if(error.code!=='ENOENT')throw error;}
console.log('Exported simulation workbook.');
