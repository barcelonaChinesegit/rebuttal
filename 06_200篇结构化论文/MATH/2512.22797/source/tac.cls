%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% tac.cls for use by TAC authors
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Copyright 2024 by The Editors of Theory and Applications of Categories
%
% This work may be distributed and/or modified under the
% conditions of the LaTeX Project Public License, either version 1.3
% of this license or (at your option) any later version.
% The latest version of this license is in
%   http://www.latex-project.org/lppl.txt
% and version 1.3 or later is part of all distributions of LaTeX
% version 2005/12/01 or later.
%
% This work has the LPPL maintenance status `maintained'.
%
% The Current Maintainer of this work is Geoff Cruttwell, Managing Editor.
%
% This work consists of the file tac.cls.


\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{tac}[2023/03/06]

\LoadClass[12pt]{article}

\DeclareOption{compromisepaper}
   {\setlength\paperheight {11.4in}%
    \setlength\paperwidth  {8.25in}}
\ProcessOptions\relax
\usepackage{xspace,mathrsfs}

\setcounter{tocdepth}{1}
\def\tableofcontents{\section*{Contents\@mkboth{CONTENTS}{CONTENTS}}
 \@starttoc{toc}}
\def\l@part#1#2{\addpenalty{\@secpenalty}
 \addvspace{2.25em plus 1\p@} \begingroup
 \@tempdima 3em \parindent \z@ \rightskip \@pnumwidth \parfillskip
-\@pnumwidth
 {\large \textbf \leavevmode #1\hfil \hbox to\@pnumwidth{\hss #2}}\par
 \nobreak \endgroup}
\def\l@section#1#2{\addpenalty{\@secpenalty} \addvspace{0em}%{1.0em plus 1\p@} mod 00-4-15
\@tempdima 1.5em \begingroup
 \parindent \z@ \rightskip \@pnumwidth
 \parfillskip -\@pnumwidth
 \textbf \leavevmode \advance\leftskip\@tempdima \hskip -\leftskip #1\nobreak\hfil
\nobreak\hbox to\@pnumwidth{\hss #2}\par
 \endgroup}

%%%%%%%%%%%% Style parameters
\lineskip 1pt
\normallineskip 1pt
\def\baselinestretch{1}
\marginparsep 10pt
\topmargin 0pt
\headheight 12pt
\headsep 15pt
\topskip = 0pt
\footskip 20pt
\textheight = 8.5in
\textwidth 6.3in
\oddsidemargin0pt
\evensidemargin0pt

%%%%%%%%%%%%%%%% Basic formatting

% Add a period after (sub)section numbers.
\def\@seccntformat#1{\csname the#1\endcsname.\kern.5em}



\def\section{\@startsection {section}{1}{\z@}{-4ex plus -1ex minus
-.2ex}{1.75ex plus .2ex}{\large}}
\def\@subsection{\@startsection{subsection}{2}{\z@}{-1.5ex plus -1ex
minus  -.2ex}{-0.3em plus -0.1em minus
-.1em}{\normalfont\normalsize\scshape}}
\def\@subsubsection{\@startsection{subsubsection}{3}{\z@}{-1.25ex plus
-1ex minus-.2ex}{-0.3em plus -.1em minus -.1em}%
{\normalfont\normalsize\scshape}}

 % The following code is to add a period at the end of any sub(sub)section
 % title not otherwise punctuate.  \smartperiod looks at the spacefactor at
 % the end of the title, which is > 1000 for punctuation and = 1000 for all
 % others.  Two warnings: It doesn't work if the header is separated, which
 % is not the case in tac.cls and it doesn't work if you use \frenchspacing
 % which sets all the \sfcodes to 1000, also not used here. Start by
 % undoing the kludge Knuth did to avoid an unlikely problem.  Note that
 % the bibliographic code includes \frenchspacing.
 \sfcode`\A=1000
 \sfcode`\B=1000
 \sfcode`\C=1000
 \sfcode`\D=1000
 \sfcode`\E=1000
 \sfcode`\F=1000
 \sfcode`\G=1000
 \sfcode`\H=1000
 \sfcode`\I=1000
 \sfcode`\J=1000
 \sfcode`\K=1000
 \sfcode`\L=1000
 \sfcode`\M=1000
 \sfcode`\N=1000
 \sfcode`\O=1000
 \sfcode`\P=1000
 \sfcode`\Q=1000
 \sfcode`\R=1000
 \sfcode`\S=1000
 \sfcode`\T=1000
 \sfcode`\U=1000
 \sfcode`\V=1000
 \sfcode`\W=1000
 \sfcode`\X=1000
 \sfcode`\Y=1000
 \sfcode`\Z=1000
\def\smartperiod{\ifnum\the\spacefactor=1000 .\fi}
\def\@starsubsection#1{\@subsection*{#1\smartperiod\ }}
\def\@nostarsubsection#1{\@subsection{#1\smartperiod}}
\def\subsection{\@ifstar{\@starsubsection}{\@nostarsubsection}}
\def\@starsubsubsection#1{\@subsubsection*{#1\smartperiod\ }}
\def\@nostarsubsubsection#1{\@subsubsection{#1\smartperiod}}
\def\subsubsection{\@ifstar{\@starsubsubsection}{\@nostarsubsubsection}}

\def\paragraph{\@startsection
     {paragraph}{4}{\z@}{1ex plus1ex minus.2ex}{-.5em
     plus -.5em minus -.1em}{\reset@font \normalsize\bf}}
\def\subparagraph{\@startsection
     {subparagraph}{4}{\parindent}{.5ex plus .5ex minus
     .2ex}{-.5em plus -.5em minus -.1em}{\reset@font\normalsize\bf}}
\def\appendix{\par
  \setcounter{section}{0}
  \setcounter{subsection}{0}
  \def\thesection{\Alph{section}}}



 % The next four lines allow you to start a theorem by giving credit (or
 % naming it) by a parenthetical note that will set in upright font and
 % enclosed by square brackets.  The syntax is \theorem[...] followed by
 % the statement of the theorem.  If this parenthetical material iteslf
 % contains square brackets, then it must be enclosed in braces.  This is
 % likeliest to occur using \cite[..]{..} in which case the syntax
 % that works is \theorem[{\cite[..]{..}..}], although
 % \theorem[{\cite[..]{..}}..] will also work.  If you do
 % \theorem[\cite{..}] or \theorem[{\cite[..]{..}}] you will _not_ get two
 % pairs of brackets.  Of course, all this works with any theorem like
 % environments and with the latex \begin..\end versions.

\def\@credit[#1]{\expandafter\@@credit\@firstofone#1\@@nil}
\def\@@credit{\@ifnextchar\cite{\@@@credit}{\@@@@credit}}
\def\@@@credit#1\@@nil{{\rm#1}}
\def\@@@@credit#1\@@nil{{\rm[#1]}}

\def\state#1{\subsection{\sc#1}%
\begingroup\em\@ifnextchar[{\@credit}{}}
 \def\staterm#1{\subsection{\sc#1}
\begingroup\@ifnextchar[{\@credit}{}}
\def\endstate{\endgroup\par\addvspace{\medskipamount}}

\def\thirdleveltheorems{%
\def\state##1{\subsubsection{\sc##1}%
\begingroup\em\@ifnextchar[{\@credit}{}}
 \def\staterm##1{\subsubsection{\sc##1}
\begingroup\@ifnextchar[{\@credit}{}}}


\def\firstleveltheorems{%
\def\section{\@startsection {section}{1}{\z@}{-1.5ex plus -1ex
minus  -.2ex}{-1em plus -0.4em minus
-.4em}{\normalfont\normalsize\scshape}}
\def\state##1{\section{\sc##1}%
\begingroup\em\@ifnextchar[{\@credit}{}}
 \def\staterm##1{\subsubsection{\sc##1}
\begingroup\@ifnextchar[{\@credit}{}}}

\def\theoremstyle#1{\def\next{#1}\def\nextt{plain}
\ifx\next\nextt\relax\let\@state\state\else\let\@state\staterm\fi}
\def\newtheorem#1{\@ifnextchar[{\@newthm{#1}}{\@newthm{#1}[]}}
\def\newtheoremrm#1{\@ifnextchar[{\@newthmrm{#1}}{\@newthmrm{#1}[]}}
\def\@newthm#1[#2]#3{\@ifnextchar[{\@@newthm{#1}[#2]{#3}}{\@@newthm{#1}[#2]{#3}[ ]}}
\def\@newthmrm#1[#2]#3{\@ifnextchar[{\@@newthmrm{#1}[#2]{#3}}{\@@newthmrm{#1}[#2]{#3}[ ]}}

\def\@@newthm#1[#2]#3[#4]{\expandafter\def\csname #1\endcsname{%
\state{#3.}\@ifnextchar[{\@credit}{}}%
 \expandafter\let\csname
     end#1\endcsname\endstate}

\def\@@newthmrm#1[#2]#3[#4]{\expandafter\def\csname #1\endcsname{%
\staterm{#3.}\@ifnextchar[{\@credit}{}}%
 \expandafter\let\csname
     end#1\endcsname\endstate}

\newtheorem{theorem}{Theorem}
\newtheorem{proposition}{Proposition}
\newtheorem{corollary}{Corollary}
\newtheorem{lemma}{Lemma}
\newtheorem{definition}{Definition}
\newtheorem{scholium}{Scholium}
\newtheorem{assumption}{Assumption}

\newtheoremrm{remark}{Remark}
\newtheoremrm{example}{Example}
\newtheoremrm{remarks}{Remarks}
\newtheoremrm{examples}{Examples}
\newtheoremrm{notation}{Notation}

\def\substate#1{\subsubsection*{\textit{#1}}}


\def\Pr@@f{\subsubsection*{\textsc{Proof.}}}
\def\pr@@f[#1]{\subsubsection*{{\textsc{Proof}} #1}}
\def\proof{\@ifnextchar[{\pr@@f}{\Pr@@f}}     %

 % \def\proofof[#1]{\subsubsection*{{\textsc{Proof of #1}}}}


\def\Pr@@fsk{\subsubsection*{\textsc{Sketch of Proof.}}}
\def\pr@@fsk[#1]{\subsection*{{\textsc{Sketch of Proof}} #1}}
\def\proofsk{\@ifnextchar[{\pr@@fsk}{\Pr@@fsk}}

\def\pushright#1{{%        set up
   \parfillskip=0pt            % so \par doesnt push \square to left
   \widowpenalty=10000         % so we dont break the page before \square
   \displaywidowpenalty=10000  % ditto
   \finalhyphendemerits=0      % TeXbook exercise 14.32
   \leavevmode                 % \nobreak means lines not pages
   \unskip                     % remove previous space or glue
   \nobreak                    % don't break lines
   \hfil                       % ragged right if we spill over
   \penalty50                  % discouragement to do so
   \hskip.2em                  % ensure some space
   \null                       % anchor following \hfill
   \hfill                      % push \square to right
   {#1}                        % the end-of-proof mark (or whatever)
   \par}}                      % build paragraph

\newbox\@endproofbox
\setbox\@endproofbox\hbox{\vrule width5pt height 5pt depth 0pt}
\def\endproofbox{\copy\@endproofbox}
\def\endproof{\pushright{\endproofbox}%
\penalty-700 \par\addvspace{\medskipamount}}

\def\endproofsk{\pushright{\endproofbox}%
\penalty-700 \par\addvspace{\medskipamount}}

%%%%%%%%%%%%%% Header things
% The following are to produce the page one headers and footnotes
% Note that there must be two passes to get the page numbers correct
% AMS classification, thanks, keywords and revision dates are optional.
% The others are required.

\newif\ifthanks
\newif\ifkeywords
\newif\ifamsclass
\newif\ifdedication
\newif\ifeaddress


\def\@title{\relax}
\def\@author{\relax}
\def\@cauthor{\relax}
\def\runningauthor{\relax}
\def\runningtitle{\relax}
\def\@num{0}
\def\@copryear{\the\year}
\def\@address{\relax}
\def\@eaddress{\relax}
\def\@thanks{\relax}
\def\@keywords{\relax}
\def\@amsclass{\relax}
\def\@runningoddhead{\relax}
\def\@runningevenhead{\relax}
\def\@dedication{\relax}

 \def\@uclcnotmath#1#2#3#4{\begingroup
       #1%
       \def\({$}\let\)\(%$
       \def\NoCaseChange##1{\noexpand\NoCaseChange{\noexpand##1}}
       \@nonchangecase\label
       \@nonchangecase\ref
       \@nonchangecase\ensuremath
       \def\cite##1##{\toks@{\noexpand\cite##1}\@citex}%
       \def\@citex##1{\NoCaseChange{\the\toks@{##1}}}%
       \def\reserved@a##1##2{\let#2\reserved@a}%
       \expandafter\reserved@a\@uclclist\reserved@b{\reserved@b\@gobble}%
       \protected@edef\reserved@a{\endgroup
           \noexpand\@skipmath#3#4$\valign$}%
       \reserved@a}
 \def\@nonchangecase#1{\def#1##1{\NoCaseChange{#1{##1}}}}
 \let\NoCaseChange\@firstofone
 \def\@skipmath#1#2$#3${%
   \@skip@nonchangecase#1#2\NoCaseChange\valign
   \ifx\valign#3%
   \else
     $#3$%
     \expandafter\@skipmath\expandafter#1%
   \fi}
 \def\@skip@nonchangecase#1#2\NoCaseChange#3{%
   #1{#2}%
   \ifx\valign#3%
   \else
     #3%
     \expandafter\@skip@nonchangecase\expandafter#1%
   \fi}
 \DeclareRobustCommand\MakeTextUppercase{%
   \@uclcnotmath{\def\i{I}\def\j{J}}{##1##2}\uppercase}
 \protected@edef\MakeTextUppercase#1{\MakeTextUppercase{#1}}
 \DeclareRobustCommand\MakeTextLowercase{%
   \@uclcnotmath{}{##2##1}\lowercase}
 \protected@edef\MakeTextLowercase#1{\MakeTextLowercase{#1}}

\def\dedication#1{\def\@dedication{{\let\cr=\\ \def\\{\protect\cr[1\p@]}
\large\textit{#1}}}\dedicationtrue}

% 01-12-14 for multiple emails
\def\CR{\\\phantom{\rm Email: }}

\long\def\address#1{\global\def\@address{{\par\addvspace{12\p@}
\baselineskip11.5pt\parindent0pt
\let\newline=\par
\noindent\textit{#1} \\ %\vspace{5pt}
\ifeaddress Email: \texttt \@eaddress\fi }}}
\def\eaddress#1{\def\@eaddress{#1}\eaddresstrue}

{\catcode`\/=\active\gdef/{\char47\penalty-100 }
 \catcode`\.=\active \gdef.{\char46\penalty-100 }
 \catcode`\_=\active \gdef_{\char95\penalty-100 }
}
\def\url{%
   \bgroup
       \catcode`\/=\active
       \catcode`\.=\active
       \catcode`\_=\active
       \def~{$\sim$}\@url}
\def\@url#1{\texttt{#1}\egroup}


\def\copyrightyear#1{\def\@copryear{{#1}}}
\def\keywords#1{\def\@keywords{Key words and phrases: #1.}\keywordstrue}
\def\amsclass#1{\def\@amsclass{2020 Mathematics Subject
Classification: #1.}\amsclasstrue}
\let\subjclass\amsclass
\def\@@thanks[#1]#2{\def\thempfn{}\footnotetext{\thmark{#1}#2}}
\def\@@@thanks#1{\def\@thanks{#1}\thankstrue}
\def\thanks{\@ifnextchar[{\@@thanks}{\@@@thanks}}
\def\thmark#1{${}^{#1)}$}

%%%%%%%%%%% Fancy headings
\@twosidetrue

% fancyheadings.sty version 1.1
% Fancy headers and footers.
% Piet van Oostrum, Dept of Computer Science, University of Utrecht
% Padualaan 14, P.O. Box 80.089, 3508 TB Utrecht, The Netherlands
% Telephone: +31-30-531806. piet@cs.ruu.nl (mcvax!hp4nl!ruuinf!piet)
% Sep 23, 1992.

\def\lhead{\@ifnextchar[{\@xlhead}{\@ylhead}}
\def\@xlhead[#1]#2{\gdef\@elhead{#1}\gdef\@olhead{#2}}
\def\@ylhead#1{\gdef\@elhead{#1}\gdef\@olhead{#1}}

\def\chead{\@ifnextchar[{\@xchead}{\@ychead}}
\def\@xchead[#1]#2{\gdef\@echead{#1}\gdef\@ochead{#2}}
\def\@ychead#1{\gdef\@echead{#1}\gdef\@ochead{#1}}

\def\rhead{\@ifnextchar[{\@xrhead}{\@yrhead}}
\def\@xrhead[#1]#2{\gdef\@erhead{#1}\gdef\@orhead{#2}}
\def\@yrhead#1{\gdef\@erhead{#1}\gdef\@orhead{#1}}

\def\lfoot{\@ifnextchar[{\@xlfoot}{\@ylfoot}}
\def\@xlfoot[#1]#2{\gdef\@elfoot{#1}\gdef\@olfoot{#2}}
\def\@ylfoot#1{\gdef\@elfoot{#1}\gdef\@olfoot{#1}}

\def\cfoot{\@ifnextchar[{\@xcfoot}{\@ycfoot}}
\def\@xcfoot[#1]#2{\gdef\@ecfoot{#1}\gdef\@ocfoot{#2}}
\def\@ycfoot#1{\gdef\@ecfoot{#1}\gdef\@ocfoot{#1}}

\def\rfoot{\@ifnextchar[{\@xrfoot}{\@yrfoot}}
\def\@xrfoot[#1]#2{\gdef\@erfoot{#1}\gdef\@orfoot{#2}}
\def\@yrfoot#1{\gdef\@erfoot{#1}\gdef\@orfoot{#1}}

\newdimen\headwidth
\newif\if@fancyplain \@fancyplainfalse
\def\fancyplain#1#2{\if@fancyplain#1\else#2\fi}


\lhead[\fancyplain{}{\sl\rightmark}]{\fancyplain{}{\sl\leftmark}}
%  i.e. empty on ``plain'' pages \rightmark on even, \leftmark on odd pages
\chead{}
\rhead[\fancyplain{}{\sl\leftmark}]{\fancyplain{}{\sl\rightmark}}
%  i.e. empty on ``plain'' pages \leftmark on even, \rightmark on odd pages
\lfoot{}
\cfoot{\rm\thepage} % page number
\rfoot{}

% Put together a header or footer given the left, center and
% right text, fillers at left and right and a rule.
% The \lap commands put the text into an hbox of zero size,
% so overlapping text does not generate an errormessage.

\def\@fancyhead#1#2#3#4#5{#1\hbox to\headwidth{\vbox{\hbox
{\rlap{\parbox[b]{\headwidth}{\raggedright#2\strut}}\hfill
\parbox[b]{\headwidth}{\centering#3\strut}\hfill
\llap{\parbox[b]{\headwidth}{\raggedleft#4\strut}}} %\headrule}}#5}
}}#5}


\def\@fancyfoot#1#2#3#4#5{#1\hbox to\headwidth{\vbox{ %\footrule
\hbox{\rlap{\parbox[t]{\headwidth}{\raggedright#2\strut}}\hfill
\parbox[t]{\headwidth}{\centering#3\strut}\hfill
\llap{\parbox[t]{\headwidth}{\raggedleft#4\strut}}}}}#5}


\def\ps@fancy{
\let\@mkboth\markboth
\@ifundefined{chapter}{\def\sectionmark##1{\markboth
{\uppercase{\ifnum \c@secnumdepth>\z@
 \thesection\hskip 1em\relax \fi ##1}}{}}
\def\subsectionmark##1{\markright {\ifnum \c@secnumdepth >\@ne
 \thesubsection\hskip 1em\relax \fi ##1}}}
{\def\chaptermark##1{\markboth {\uppercase{\ifnum \c@secnumdepth>\m@ne
 \@chapapp\ \thechapter. \ \fi ##1}}{}}
\def\sectionmark##1{\markright{\uppercase{\ifnum \c@secnumdepth >\z@
 \thesection. \ \fi ##1}}}}
\ps@@fancy
\headwidth\textwidth}
\def\ps@fancyplain{\ps@fancy \let\ps@plain\ps@plain@fancy}
\def\ps@plain@fancy{\@fancyplaintrue\ps@@fancy}
\def\ps@@fancy{
\def\@oddhead{\@fancyhead\relax\@olhead\@ochead\@orhead\hss}
\def\@oddfoot{\@fancyfoot\relax\@olfoot\@ocfoot\@orfoot\hss}
\def\@evenhead{\@fancyhead\hss\@elhead\@echead\@erhead\relax}
\def\@evenfoot{\@fancyfoot\hss\@elfoot\@ecfoot\@erfoot\relax}
}
\def\maketitle{\par
 \begingroup
 \def\thefootnote{\fnsymbol{footnote}}
 \def\@makefnmark{\hbox
 to\z@{$^{\@thefnmark}$\hss}}
 \global\@topnum\z@ \@maketitle \thispagestyle{plain}
 \endgroup
 \setcounter{footnote}{0}
 \let\@maketitle\relax
{\def\thempfn{}
\ifthanks\footnotetext{\@thanks}\fi
\ifamsclass\footnotetext{\@amsclass}\fi
\ifkeywords\footnotetext{\@keywords}\fi
% mod 2001-7-7
\def\relaxp[##1]{\relax}
\def\footnotemark{\@ifnextchar[{\relaxp}{\relax}}
\footnotetext{\copyright\ \@cauthor,\ \@copryear.
Permission to copy for private use granted.}
}}
\pagestyle{fancyplain}


\def\Uppercase#1{\let\i=I\let\j=J\def\ss{SS}\uppercase{#1}}
\let\MakeUppercase=\Uppercase
% The next two lines specify the font and size for the headers (and footer)
\def\headstyle#1{\let\\=\relax\footnotesize\MakeUppercase{#1}}
\def\thefnpage{{\rm\thepage}}

%\headrulewidth0pt
\headheight 14.5pt
\lhead[\fancyplain{}{\thefnpage}]{\fancyplain{}{}}
\chead[\fancyplain{}{\runningauthor}]{\fancyplain{}{\runningtitle}}
\rhead[]{\fancyplain{}{\thefnpage}}
\lfoot{}
\cfoot[\fancyplain{\thefnpage}{}]{\fancyplain{\thefnpage}{}}
\rfoot{}


\def\@@title[#1]#2{\def\@title{{\let\cr=\\ \def\\{\protect\cr[1\p@]}
\large\MakeUppercase{#2}}}\def\runningtitle{\headstyle{#1}}}
\def\@@@title#1{\def\@title{{\let\cr=\\ \def\\{\protect\cr[1\p@]}
\large\MakeUppercase{#1}}}\def\runningtitle{\headstyle{#1}}}
\def\title{\@ifnextchar[{\@@title}{\@@@title}}


\def\@@author[#1]#2{\def\@author{\MakeUppercase{#2}}\def\@cauthor
{\def\thmark####1{\relax}#2}\def\runningauthor{\headstyle{#1}}}
\def\@@@author#1{\def\@author{\MakeUppercase{#1}}\def\@cauthor
{\def\thmark####1{\relax}#1} \def\runningauthor
{\def\thmark####1{\relax}\headstyle{#1}}}
\def\author{\@ifnextchar[{\@@author}{\@@@author}}
\def\cauthor#1{\def\@cauthor{#1}}

%%% end of fancyheadings mods


\def\@maketitle{\newpage\vspace*{12\p@}
{\topsep\z@ \partopsep\z@
\begin{center}
\ifdedication
   \@title\\[12\p@]
   \@dedication\\[18\p@]
\else
   \@title\\[14\p@]
\fi
\@author
\end{center}}
\vskip24\p@}

\def\abstractname{Abstract}
\def\abstract{\bgroup\par
\footnotesize\begin{list}{}{\rightmargin=13mm \leftmargin=13mm
\parsep5\p@ \listparindent=\z@ \topsep=\z@\partopsep=\z@}
\item\leavevmode% \hbox to 1em{\hss} deleted indent 00-1-20
{\textsc{\abstractname.}}\hskip 1em}
\def\endabstract{\end{list}\par\egroup}



%Note that this is a redefinition.  Its purpose is to compile the
%label lastpage so that we can get the page numbers right.
%It also adds the authors' address

\AtEndDocument{%
% mod 99/12/4 - suppress breaks, label inside
% mod 2015-02-09
\nopagebreak[4]%
\@address
\label{lastpage}%
\nopagebreak[4]%
}

%%%%%%%%%%% Bibliographical styles
\def\thebibliography#1{\section*{References\@mkboth
 {REFERENCES}{REFERENCES}}\list
 {[\arabic{enumi}]}{\settowidth\labelwidth{[#1]}\leftmargin\labelwidth
 \advance\leftmargin\labelsep
 \usecounter{enumi}}
 \def\newblock{\hskip .11em plus .33em minus .07em}
 \sloppy\clubpenalty4000\widowpenalty4000
 \sfcode`\.=1000\relax}
\let\endthebibliography=\endlist


% Below are the codes for the two reference styles.  They can be called by
% \begin{references} ... \end{references} and \begin{references*} ...
% \end{references*} .  In addition, the first can be called by \references
% ... \endreferences .

\newdimen\twlrm
\newdimen\refindent \refindent 8mm
\def\references{%
%\fontdimen2\twlrm=4.3pt% space instead of 3.91663
%\fontdimen3\twlrm=4.2pt%stretch instead of 1.95831
%\fontdimen4\twlrm=1.7pt%shrink instead of 1.30554
\section*{References}
\sloppy % RR deleted 2008-01-26 \footnotesize
\begin{list}{}
{\leftmargin\refindent \itemindent-\refindent \itemsep2pt \topsep0pt}}
\def\endreferences{\end{list}}

\newcounter {reflister}
\expandafter\def\csname references*\endcsname {%
%\fontdimen2\twlrm=4.3pt% space instead of 3.91663
%\fontdimen3\twlrm=4.2pt%stretch instead of 1.95831
%\fontdimen4\twlrm=1.7pt%shrink instead of 1.30554
\section*{References}
\sloppy\footnotesize
\begin{list}{{\textrm[\arabic{reflister}]}}{\usecounter{reflister}}
{\leftmargin\refindent \itemindent-\refindent \itemsep2pt \topsep0pt}}
\expandafter\let\csname endreferences*\endcsname=\endreferences


 % Here is a third reference style.  An alternative to \thebibliography, it
 % is intended to be used as follows.
 %
 % and then \cite{A} will give [Author (year)]

\def\refs{\bgroup\section*{References\@mkboth{REFERENCES}
{REFERENCES}}\def\@biblabel##1{\relax}\frenchspacing\list{}{
 \leftmargin2em \itemindent-2em}
 \def\newblock{\hskip .11em plus .33em minus .07em}
 \sloppy\clubpenalty4000\widowpenalty4000
 \sfcode`\.=1000\relax}
\def\endrefs{\endlist\egroup}

\def\aref{\bgroup\section*{Reference\@mkboth{REFERENCE}
{REFERENCE}}\def\@biblabel##1{\relax}\frenchspacing\list{}{
 \leftmargin2em \itemindent-2em}
 \def\newblock{\hskip .11em plus .33em minus .07em}
 \sloppy\clubpenalty4000\widowpenalty4000
 \sfcode`\.=1000\relax}
\def\endaref{\endlist\egroup}

 % The \tcite below allows one to put a citation within the optional
 % argument to a theorem or like, including a page citation.  If there is a
 % page citation (inside []), then the entire citation must be enclosed in
 % braces.

\def\tcite{\def\@cite##1##2{{##1\if@tempswa , ##2\fi}}\cite}

% The following is the content of breakcite.sty to allow breaking of
% citations.  This originally caused an obscure error that the latex
 % team has fixed, along with the problem of breaking.  The following is
 % exactly what is found in the current (but not older) latex.ltx


\def\@citex[#1]#2{\leavevmode
  \let\@citea\@empty
  \@cite{\@for\@citeb:=#2\do
    {\@citea\def\@citea{,\penalty\@m\ }%
     \edef\@citeb{\expandafter\@firstofone\@citeb\@empty}%
     \if@filesw\immediate\write\@auxout{\string\citation{\@citeb}}\fi
     \@ifundefined{b@\@citeb}{\hbox{\reset@font\bfseries ?}%
       \G@refundefinedtrue
       \@latex@warning
         {Citation `\@citeb' on page \thepage \space undefined}}%
       {{\csname b@\@citeb\endcsname}}}}{#1}}

% Modification of the `plain' definition, taken over by latex.  Note the
% failure to parametrize the definition, one of the many such that testify
% to Knuth's conception of plain as a provisional package.

\def\footnoterule{%\kern-3\p@
  \hrule width 1truein \kern 2.6\p@} % the \hrule is .4\p@ high

% old font commands from article.cls

\DeclareOldFontCommand{\rm}{\normalfont\rmfamily}{\mathrm}
\DeclareOldFontCommand{\sf}{\normalfont\sffamily}{\mathsf}
\DeclareOldFontCommand{\tt}{\normalfont\ttfamily}{\mathtt}
\DeclareOldFontCommand{\bf}{\normalfont\bfseries}{\mathbf}
\DeclareOldFontCommand{\it}{\normalfont\itshape}{\mathit}
\DeclareOldFontCommand{\sl}{\normalfont\slshape}{\@nomath\sl}
\DeclareOldFontCommand{\sc}{\normalfont\scshape}{\@nomath\sc}
\DeclareRobustCommand*\cal{\@fontswitch\relax\mathcal}
\DeclareRobustCommand*\mit{\@fontswitch\relax\mathnormal}


% Follows are a small number of procedures I have personally found very
% useful.  The first five define new math operations like Hom.  In the
% first, the word is spaced like a mathop and is used if there are to be
% arguments.  It is better not used if, like Hom, it is followed by an
% opening paranthesis.  The next two are without the spacing and are used
% for boldface, roman face, resp.  The usage is: \mathrm{Hom} that defines
% a new macro \Hom that puts the word Hom in ordinary type.

% replaced 2004-03-24 to allow an optional alternate name.  For example,
% \mathopdef[hom]{Hom} creates a macro called \hom that produces
% \mathop{\rm Hom}\nolimits.

\DeclareFontFamily{OT1}{pzc}{}
\DeclareFontShape{OT1}{pzc}{m}{it}%
     {<-> s * [1.15] pzcmi7t}{}
\DeclareMathAlphabet{\mathzc}{OT1}{pzc}{m}{it}
\DeclareSymbolFont{script}{OT1}{pzc}{m}{it}
\DeclareMathAlphabet{\mathcmssbx}{OT1}{cmss}{bx}{n}

\def\@mathopdef[#1]#2{\expandafter\def\csname#1\endcsname
{\mathop{\rm{}#2}\nolimits\xspace}}
\def\@mathoplsdef[#1]#2{\expandafter\def\csname#1\endcsname
 {\mathop{{}#2}\xspace}}
\def\@mathbfdef[#1]#2{\expandafter\def\csname#1\endcsname
 {{\rm\bf#2}\xspace}}
\def\@mathrmdef[#1]#2{\expandafter\def\csname#1\endcsname
{{\ensuremath{\rm#2}}\xspace}}
\def\@mathsfdef[#1]#2{\expandafter\def\csname#1\endcsname
{{\ensuremath{\sf#2}}\xspace}}
\def\@mathfkdef[#1]#2{\expandafter\def\csname#1\endcsname
{\ensuremath{\frak{#2}}\xspace}}
\def\@mathzcdef[#1]#2{\expandafter\def\csname#1\endcsname
{{\ensuremath{\mathzc{#2}}}\xspace}}
\def\@mathcaldef[#1]#2{\expandafter\def\csname#1\endcsname
{{\ensuremath{\mathcal{#2}}}\xspace}}
\def\@mathssbxdef[#1]#2{\expandafter\def\csname#1\endcsname
{{\ensuremath{\mathcmssbx{#2}}}\xspace}}
\def\@mathrsfsdef[#1]#2{\expandafter\def\csname#1\endcsname
{{\ensuremath{\mathscr{#2}}}\xspace}}

\def\mathopdef{\@dblarg\@mathopdef}
\def\mathopsldef{\@dblarg\@mathopsldef}
\def\mathbfdef{\@dblarg\@mathbfdef}
\def\mathrmdef{\@dblarg\@mathrmdef}
\def\mathsfdef{\@dblarg\@mathsfdef}
\def\mathfkdef{\@dblarg\@mathfkdef}
\def\mathzcdef{\@dblarg\@mathzcdef}
\def\mathssbxdef{\@dblarg\@mathssbxdef}
% next lines added 2009-10-25
\def\mathcaldef{\@dblarg\@mathcaldef}
% replaced 2015-06-29
% put back 2015-08-02
\def\mathrsfsdef{\@dblarg\@mathrsfsdef}
%\DeclareSymbolFont{rsfscript}{OMS}{rsfs}{m}{n}
%\DeclareSymbolFontAlphabet{\mathrsfs}{rsfscript}
%\def\@mathrsfsdef[#1]#2{\expandafter\def\csname#1\endcsname
%{{\ensuremath{\mathrsfs{#2}}}\xspace}}


\def\mld#1$${\null\,\vcenter\bgroup\def\\{\cr&}\openup9pt\m@th
\ialign\bgroup\strut\hfil$\displaystyle{##}$%
&$\displaystyle{{}##}$\hfil\crcr #1
\crcr\egroup\egroup\,$$}
\def\mldepf#1$${\null\,\vbox\bgroup\def\\{\cr&}\openup9pt\m@th
\ialign\bgroup\strut\hfil$\displaystyle{##}$%
&$\displaystyle{{}##}$\hfil\crcr #1
\crcr\egroup\egroup\,\eqno{\endproofbox}$$}
\let\emld\relax % for compatibility with old code

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Here is a typical usage of \mld (multi-line display)          %%
%%                                                               %%
%% The pattern is                                                %%
%% $$\mld formula 1 & formula 2 \\                               %%
%%                    formula 3 \\                               %%
%%                    ..........\\                               %%
%%                    formula n $$                               %%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\DeclareFontShape{OMX}{cmex}{m}{n}{%
      <-8>sfixed * cmex7
      <8> cmex8
      <9> cmex9
      <10> <10.95> <12> <14.4> <17.28> <20.74> <24.88>cmex10
       }{}
\DeclareSymbolFont{largesymbols}{OMX}{cmex}{m}{n}
\newdimen\big@size
\addto@hook\every@math@size{\setbox\z@\vbox{\hbox{$($}\kern\z@}%
   \global\big@size 1.2\ht\z@}
\def\bBigg@#1#2{%
   {\hbox{$\left#2\vcenter to#1\big@size{}\right.\n@space$}}}
\def\big{\bBigg@\@ne}
\def\Big{\bBigg@{1.5}}
\def\bigg{\bBigg@\tw@}
\def\Bigg{\bBigg@{2.5}}
\def\edot{\vrule height .5pt width .5pt depth 0pt\kern1.5pt}
\def\eat{\raise1.4pt\hbox{\emph{\footnotesize a}}\llap 0\kern.5pt}

\usepackage[pdfusetitle,linktoc=all,colorlinks=true]{hyperref}
\hypersetup{allcolors=[rgb]{0.1,0.1,0.4}}

\endinput














