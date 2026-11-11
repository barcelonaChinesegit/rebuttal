%% Class to render PTA paper
%% Please see the informations, terms and conditions at the end
%% of this file

\def \pta@Version     {1.0.7}
\def \pta@Date        {2019/09/26}

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ptapap}%
    [\pta@Date v\pta@Version\space Polish Astronomical Society]

\def \ptaTraceAll{\tracingall\tracingcommands=3\tracinglostchars=2\relax}

\RequirePackage{xparse}
\RequirePackage{trimspaces}
\RequirePackage{xstring}
\RequirePackage[T1]{fontenc}
\RequirePackage{ae,aecompl}
\RequirePackage[utf8]{inputenc}
\RequirePackage{fancyhdr}
\RequirePackage{graphicx}
\RequirePackage{aas_macros}
% \RequirePackage{caption}

% aas_macros incorrectly defines \jnl@style as \let while \rm is not defined,
% we need to redefine it correctly
\def \jnl@style{\rm}
%\RequirePackage{subfigure}

% private keywords are prefixed with \pta@

\def \pta@csdef {\expandafter \def \csname}
\def \pta@csedef{\expandafter \edef \csname}


%    ****************************************
%    *               OPTIONS                *
%    ****************************************

% Option values are now declared first thing.  Defaults are set to
% 10 point, onesided, draft (ie not draft) mode (BBF 10/31/94)
\DeclareOption{draft}{\renewcommand\@draftmark{1}}
\DeclareOption{final}{\renewcommand\@draftmark{0}}
\ProcessOptions*
\LoadClass[10pt]{article}
\RequirePackage{geometry}
% \geometry{b5paper,margin=2cm,includehead,includefoot}
\geometry{papersize={168mm,244mm},
  left=2cm, right=2cm, top=2cm, bottom=2cm}

\RequirePackage[authoryear]{natbib}
\renewcommand{\bibfont}{\small}
\setlength{\bibsep}{4pt plus 2pt minus 2pt}

% Auxiliary macros

\expandafter \def
\expandafter \pta@GobbleMeaningPrefix 
             \meaning \empty
             {}


\def \pta@ProcessKeywords
    #1% #1 is the macro, it must a single token, not {tokens}
    % followed a sequence of characters ended by \relax\relax
    {\begingroup
      % #1 is applied to every keyword, i.e. anything separated by
      % a space or comma.
      \@tempcnta 0% outside {}
      \def \a{\futurelet \c \b}%
      \def \b{%
        \ifcase
           0%
           \if \c\space 1\fi
           \if ,\c      1\fi
           \if \c\relax 
               \ifnum\@tempcnta=1 1\else 2\fi\fi
           \relax
           \ifnum \@tempcnta=0%
               \aftergroup #1%
               \aftergroup {%
               \@tempcnta=1\fi
           \expandafter \A
        \or
           \ifnum \@tempcnta=1%
               \aftergroup }%
               \@tempcnta=0%
           \fi
           \expandafter \Z
        \or
           \expandafter \endgroup
        \fi
      }%
      \def \A##1{\aftergroup##1\a}%
      \def \Z{\afterassignment\a \let\c= }%
      \a
    }

% Parsing \author:
% The following forms are valid:

% \author{First Last}
% \author*{First Last}
% \author{First Last}[email@domain, http://url, AFFILKEYWORD AFFILKEYWORD2]
% \author[KEYWORDS]{First Last} is also ok
%
% the starred version of author indicates the corresponding
% author.
%
% If there is no corresponding author, the first author with an
% email is selected as corresponding. If there is no such one,
% the very first is selected as corresponding author

\newcount \NoOfAuthors
\NoOfAuthors=0
\newcount \NoOfAffiliations
\NoOfAffiliations=0
\def \CorrespondingAuthorNo{-100000}
\newif \ifpta@authoristeam \pta@authoristeamfalse

\DeclareDocumentCommand \author {s O{} m O{}}{
  \advance \NoOfAuthors 1
  \IfBooleanTF{#1}{%
    \ifnum \CorrespondingAuthorNo<0
      \edef \CorrespondingAuthorNo{\number \NoOfAuthors}
    \else
       \ClassError{ptapap}%
          {There must be only ONE corresponding author}%
          {Only one \string\author* is implemented}%
    \fi}{}%
  \begingroup
     \let \protect \@unexpandable@protect
     \edef \a{\endgroup
       \def \expandafter \noexpand \csname
         Author::\number\NoOfAuthors\endcsname
         {#3}%
       \def \expandafter \noexpand \csname
       Author::\number \NoOfAuthors::isTeam\endcsname
       {\ifpta@authoristeam 1\else 0\fi}%
     }%
  \a
  \begingroup
     \let \NoValue=\empty
     \edef \a{\endgroup\def \noexpand \tmpKeywords{#2 #4}}\a
  \pta@csedef AuthAffil::\number \NoOfAuthors\endcsname{}
  {\aftergroup \pta@ProcessKeywords
   \aftergroup \pta@SingleKeyword
   \let~\expandafter
  ~~~}~\pta@GobbleMeaningPrefix\meaning \tmpKeywords
  \relax \relax \relax
  \pta@authoristeamfalse
}
\def \team{\pta@authoristeamtrue\author}

\def \pta@EmailCS#1{%
  \ifnum #1=0
      \expandafter \pta@EmailCS \expandafter \NoOfAuthors
  \else
      Email::\number\numexpr #1\relax
  \fi}

\def \pta@undefAffil{\ClassError{ptapap}{Undefined affiliation}{}}

% Parse the keyword
% If it contains @, it's an email
% If it contains ://, it's an url
% Otherwise it's a keyword for affiliating institute.
\def \pta@SingleKeyword#1{%
  \IfSubStr{#1}{\string @}{%
    % This is an email, add it to list of emails
    \edef \next {\ifcsname \pta@EmailCS0\endcsname
      \csname \pta@EmailCS0\endcsname, \fi
      #1}
    \expandafter \let \csname \pta@EmailCS0\endcsname=\next
  }{%
    \IfSubStr{#1}{://}{%
      % This is an URL, set up a single url
      \ifcsname URL::\number \NoOfAuthors\endcsname
         \ClassError{ptapap}{Author's URL defined twice!}{}
      \else
         \pta@csedef URL::\number\NoOfAuthors\endcsname{#1}
      \fi
    }{%
      % Add affiliations
      %
      \pta@csedef AuthAffil::\number \NoOfAuthors\endcsname{%
          \csname AuthAffil::\number \NoOfAuthors\endcsname
        \pta@procAffil{#1}%
      }%
      \ifcsname Affil::#1::No\endcsname
      \else
          \advance \NoOfAffiliations 1
          \pta@csedef Affil::#1::No\endcsname{\number\NoOfAffiliations}%
          \pta@csedef Affil::\number\NoOfAffiliations::Id\endcsname {#1}%
      \fi
    }}}

\let \pta@procAffil=\relax



% Process the affiliation
% \affil[KEYWORD]{Definition}

\DeclareDocumentCommand \affil {o m}{\let\\=\relax
  \pta@csedef Affil::#1::Text\endcsname{#2}}


\renewcommand \maketitle {\par
  \vbox {\let \\=\break
    \raggedright
    \noindent \LARGE\bf
    \@title
    \setbox0=\hbox{Yy()\{\}}%
    \baselineskip=1.2\dimexpr\ht0+\dp0\relax\par
  }
  \kern 2\baselineskip
  \setbox \headtitlebox=\hbox{%
    \ifcsname @headtitle\endcsname
    \@headtitle
    \else
    \@title
    \fi}%
  \ifdim \wd \headtitlebox>0.9\hsize
      \ClassError{ptapap}{
        \ifcsname @headtitle\endcsname
          The title you provided in^^J \string\headtitle{...}^^Jis
          still too long. It must be fit into a single line.^^JIt's
          ok to provide a title in the abbreviated form,^^Jlike
          \string \headtitle{Pulsation of $\delta$ Scuti\dots}.
        \else
          The title as specified by \string\title{...} is too
          long^^Jand cannot be fit in the running head.^^JPlease
          provide the shorter version using^^J^^J \space\space\space\string
          \headtitle{abbreviated title}^^J^^Jto use in the head of article.
        \fi}{}
  \fi
  %
  %
  % Enumerate authors
  %
  \vbox{\noindent\strut\raggedright
    \count0=0
    \global\setbox\headauthorsbox=\hbox{\csname Author::1\endcsname}%
    \loop
        \advance \count0 1
        \count1=0
        \ifnum \count0>1
            \global\setbox \headauthorsbox=\hbox{%
              \unhbox \headauthorsbox
              , \csname Author::\number\count0\endcsname}%
        \fi
        \hbox{\csname Author::\number\count0\endcsname
          \def \pta@procAffil{\advance\count1 1\@gobble}%
          \csname AuthAffil::\number\count0\endcsname
          \count2=1
          \def \pta@procAffil####1{%
            \csname Affil::####1::No\endcsname
            \message{**>>1=\the\count1, 2=\the\count2 **}%
            \ifnum\count2=\count1\relax\else \cdot\fi
            \advance \count2 1
          }%
          $^{\csname AuthAffil::\number \count0\endcsname}$%
        }%
        \ifnum \count0<\NoOfAuthors
           \ifnum \count0<\numexpr \NoOfAuthors-1\relax
              ,
           \else
               \kern 0.2em\relax and~%
           \fi
        \fi
    \ifnum \count0<\NoOfAuthors
      \relax
    \repeat
    %
    \ifdim \wd\headauthorsbox>0.9\hsize
       \global\setbox\headauthorsbox=\hbox{%
          \csname Author::1\endcsname, et al.}%
    \fi
  }

  {\setbox0=\vbox{\ptapapAffiliationFont
      \kern\baselineskip
      \count0=0
      \loop
        \advance \count0 1
        \raggedright
        \noindent \parshape 1 2em \dimexpr \hsize-2em\relax
        \llap{\number\count0. }%
        \let\\=\break
        \csname Affil::%
        \csname Affil::\number\count0::Id\endcsname
        ::Text\endcsname\par
      \ifnum\count0<\NoOfAffiliations \repeat}
    \unvbox0}
  \bigskip
  \bigskip
}

\newbox \headtitlebox
\newbox \headauthorsbox

\newcommand \ptapapAffiliationFont{\fontsize{6pt}{8pt}%
  \sffamily
  \selectfont}

\newcommand \headtitle[1]{\gdef \@headtitle{#1}}

% Abstract
\renewenvironment{abstract}%
{\par\begingroup
  \leftskip=2em
  \rightskip=\leftskip
  \small
  \@afterindentfalse
  \@afterheading
}
{\par\endgroup\bigskip}

\def \ArticleFirstPage{51}


\def
\ptaFootFieldSeparator{\leavevmode\kern2pt\vrule\kern2pt\relax}

\def 
\ptaFootFieldSeparator{\leavevmode\kern2pt$\star$\kern2pt\relax}

% In the real paper this will be replaced by the concrete journal date and volume.
\edef \ptaJournalDate{\today}
\edef \ptaJournalVolume{vol.~123}
\def \next#1#2#3#4\relax{\lowercase{\edef \next{#1#2#3}}}%
\expandafter\next\ptaJournalDate\relax
\edef \ptaArticleURL{pta.edu.pl/proc/\the\year\next\the\day/123}
\edef \ptaJournalName{PTA Proceedings}

\def \ptaFooter{%
  \ifodd \thepage
    \small \ptaArticleURL\hfill
    \ptaJournalName
    \ptaFootFieldSeparator
    \ptaJournalDate
    \ptaFootFieldSeparator
    \ptaJournalVolume
    \ptaFootFieldSeparator
    \normalsize \thepage
  \else
    \thepage \small
    \ptaFootFieldSeparator
    \ptaJournalName
    \ptaFootFieldSeparator
    \ptaJournalDate
    \ptaFootFieldSeparator
    \ptaJournalVolume
    \hfill
    \ptaArticleURL\normalsize
  \fi
}

\def \ptaHeader{%
  ~\copy\ifodd \thepage
      \headtitlebox
  \else
      \headauthorsbox
  \fi~}

\fancypagestyle{firstpage}{
\fancyhf{}
\fancyfoot[C]{\ptaFooter} 
\renewcommand{\footrulewidth}{0.1pt}
\renewcommand{\headrulewidth}{0pt}
}

\fancypagestyle{regularpage}{
\fancyhf{}
\fancyfoot[C]{\ptaFooter} 
\fancyhead[C]{\ptaHeader} 
\renewcommand{\footrulewidth}{0.1pt}
\renewcommand{\headrulewidth}{0.1pt}
}
\pagestyle{regularpage}
\thispagestyle{firstpage}



% Sections and subsections

\long \def \section
{\@startsection
  {section}%
  {1}%
  {\z@}%
  {-\baselineskip}%
  {\baselineskip}%
  {\ptaStyleSection}%
}

\long \def \subsection
{\@startsection
  {subsection}%
  {2}%
  {\z@}%
  {-\baselineskip}%
  {\baselineskip}%
  {\ptaStyleSubSection}%
}


\def \ptaStyleSection{\noindent\textbf}
\def \ptaStyleSubSection{\textsl}

% VERY rough approximation of days since 1 Jan 2000
\def \pta@ApproxDays#1#2#3{\numexpr #1+
30*(#2+12*(#3-2000))\relax}


% Yes, call me crazy but, just for fun, I am implementing
% and EXPANDABLE Mouth-Of-TeX implementation of Julian Day
% The only reason to do that is getting the implementation 
% of «class is too obsolete» and it might be implemented in the
% easier way, but implementing it as Julian Day makes simply more
% fun.


% Auxiliary macro:
% -- yes, Peter Breitenlohner and Phil Taylor, we all love you
%    for your crazy integer arithmetic. Seriously, I dreamed of
%    killing all implementors of \numexpr.
%
% This macro tries to reimplement \numexpr expr1/expr2 \relax the
% proper way. The original (see my hate lines above) rounds the
% integer instead of truncating it. This one truncates.

\newcommand \truncdiv[2]{\expandafter 
     \truncdivA \expandafter {\number \numexpr
     #1/#2 \nextnumargument #1\nextnumargument #2\relax}}

% Instead of putting {\numexpr ...\relax}{\numexpr ...\relax}{...} 
% separate arguments with this macro. They will be all expanded,
% saving your stack.
% instead of {\numexpr ...\relax}{\numexpr ...\relax} put
% {\number\numexpr ... \nextnumargument ... \relax}
\newcommand \nextnumargument {%
     % make \def parser happy with proper {} balancing
     \iffalse{\fi
      \expandafter \relax
      \expandafter }%
      \expandafter {%
      \number \numexpr
      \iffalse}\fi}

\newcommand \truncdivA[3]{% #1 is result
     \numexpr \number \numexpr #1\ifnum \numexpr
     #1*#3\relax>#2-1\fi\relax\relax}

% 
% \JulianDay{YEAR}{MONTH}{DAY} (Gregorian Calendar)
% expands to a \numexpr and should be preceeded by \number
%
% The algorithm taken from:
% http://en.wikipedia.org/wiki/Julian_day#Converting_Julian_or_Gregorian_calendar_date_to_Julian_Day_Number
% or http://tinyurl.com/convert-gregorian-to-JD
\newcommand \JulianDay[3]{\numexpr
     \expandafter \JulianDayContA
     \expandafter {\number\numexpr
        #1\nextnumargument
        #2\nextnumargument
        #3\nextnumargument
        % parameter a=floor((14-month)/12): 1 for Jan,Feb, 0 otherwise
        \ifnum \numexpr #2\relax<3 1\else 0\fi\relax}\relax}

\newcommand \JulianDayContA[4]{\numexpr
     % #1 -- year
     % #2 -- month
     % #3 -- day
     % #4 -- 1 if Jan or Feb, 0 otherwise, called “a”
     \expandafter \JulianDayContB
     \expandafter {\number\numexpr
       #1\nextnumargument
       #2\nextnumargument
       #3\nextnumargument
       #4\nextnumargument
       % y = 4800+year-a
       4800+#1-#4\nextnumargument
       % m = month + 12a - 3
       #2+(12*#4)-3\relax}\relax}

\newcommand \JulianDayContB[6]{\numexpr
     % #1 -- year
     % #2 -- month
     % #3 -- day
     % #4 -- a, =1 for Jan or Feb, =0 otherwise
     % #5 -- y = 4800+year-a
     % #6 -- m = month + 12a - 3
     #3+\expandafter \truncdiv\expandafter{\number\numexpr 153*#6+2\relax}{5}+365*#5+%
     \truncdiv{#5}{4}-\truncdiv{#5}{100}+%
     \truncdiv{#5}{400}-32045\relax}

\newcommand \EditorsNote {\noindent \begingroup
    \def \next ##1/##2/##3\relax{\count0=\numexpr 
         \JulianDay{\year}{\month}{\day}-
         \JulianDay{##1}{##2}{##3}\relax
      \ifnum \count0> 3600
         \kern -2cm
         \vrule width 0.5cm~\textbf{The file ptapap.cls is
         \number\count0\relax~days old.} Get a new one:
         http://users.camk.edu.pl/chris/pta/ptapap.tar.gz~\vrule
         width 0.5cm
      \else 
       \strut \iffalse Submited on:\dots, Printed on:\dots (filled by the
         editor)\fi
      \fi}%
    \expandafter \next \pta@Date\relax\endgroup\par
}


\renewcommand{\figurename}{\small Fig.}

\def \acknowledgements #{\section*{}\vskip-2\baselineskip
\noindent \bgroup\bgroup \aftergroup \par\aftergroup \egroup
\small
{\it Acknowledgements.}\space
 \afterassignment \ignorespaces \let \bgroup=}

\let \acknowledgments = \acknowledgements


\InputIfFileExists{ptapap-local}{\relax
}%
{%
  \setcounter{page}{\ArticleFirstPage}
}


\let \oldfnum@table=\fnum@table
\let \oldfnum@figure=\fnum@figure
\def \fnum@table{\small \oldfnum@table}
\def \fnum@figure{\small \oldfnum@figure}
\renewcommand{\tablename}{Tab.}

     

     



\endinput


TERMS AND CONDITIONS:


Coding author: Krzysztof Leszczyński <chris@camk.edu.pl>

Copyright: Polish Astronomical Society – http://www.pta.edu.pl

BSD 3-clause license


Copyright (c) 2013, Polish Astronomical Society – http://www.pta.edu.pl
All rights reserved.

Redistribution and use in source and binary forms, with
or without modification, are permitted provided that the
following conditions are met:

1. Redistributions of source code must retain the above
   copyright notice, this list of conditions and the following
   disclaimer.

2. Redistributions in binary form must reproduce the above
   copyright notice, this list of conditions and the following
   disclaimer in the documentation and/or other materials
   provided with the distribution.

3. Neither the name of the Polish Astronomical Society nor the
   names of its contributors may be used to endorse or promote
   products derived from this software without specific prior
   written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

END OF TERMS AND CONDITIONS


Local Variables:
mode: latex
coding: utf-8
End:
