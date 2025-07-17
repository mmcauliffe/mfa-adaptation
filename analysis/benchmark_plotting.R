library(tidyr)
library(dplyr)
library(readr)
library(stringr)
root_dir = "/Users/michael/Documents/Data/experiments/adaptation_benchmarking/alignments"

evals = list.dirs(root_dir, recursive = F, full.names = F)

data = data.frame()

for (e in evals){
    
    print(e)
    path = file.path(root_dir, e, "alignment_reference_evaluation.csv")
    if (!file.exists(path)){
      next
    }
    print(path)
    d = read_csv(path, show_col_types = F, lazy=F)
    d$alignment_score <- as.numeric(d$alignment_score)
    d$utterance <- paste(d$file, str_replace_all(as.character(d$begin), '\\.', '-'), str_replace_all(as.character(d$end), '\\.', '-'), sep="-")
    d$evaluation = e
    data = bind_rows(data,d)
}


data <- subset(data, !is.na(data$alignment_score))
data = subset(data, word_count > 1)
data = subset(data, !(word_count == 2 & reference_phone_count == 2))

manual_parts <- subset(data, str_detect(evaluation, '_\\d'))
data <- subset(data, !str_detect(evaluation, '_\\d'))

data$evaluation = factor(data$evaluation)


data$language <- 'english'
data[str_detect(data$evaluation, "mandarin"),]$language <- 'mandarin'
data[str_detect(data$evaluation, "arpa"),]$language <- 'arpa'
data[str_detect(data$evaluation, "czech"),]$language <- 'czech'
data[str_detect(data$evaluation, "german"),]$language <- 'german'
data$language <- factor(data$language)

data$adaptation <- 'none'
data[str_detect(data$evaluation, "adapted"),]$adaptation <- 'base'
data[str_detect(data$evaluation, "manual"),]$adaptation <- 'manual'
#data[str_detect(data$evaluation, "mixed"),]$adaptation <- 'mixed'
data$adaptation <- factor(data$adaptation, levels=c('none', 'base', 'manual', 'mixed'))

plotData <- summarySE(data=data, measurevar = 'alignment_score', groupvars=c('evaluation'))
baseplotData <- summarySE(data=data, measurevar = 'alignment_score', groupvars=c('language', 'adaptation'))

t = speaker_subsets %>% subset(language == 'english' & adaptation == 'base' & speaker == 's37')
t2 = speaker_subsets %>% subset(num_speakers == 34 & language == 'mandarin' & adaptation == 'base')

t3 = t %>% group_by(utterance, num_speakers) %>% summarise(alignment_score=mean(alignment_score)) %>% group_by(utterance) %>% summarise(alignment_score=mean(alignment_score))
t2 %>% group_by(speaker) %>% summarise(mean(alignment_score))

ggplot(aes(x=num_speakers, y=mean * 1000, color=adaptation), data=speakerplotData) + geom_point(size = 5) +
  geom_errorbar(aes(ymin = (mean - ci) * 1000, ymax = (mean + ci)* 1000),size=2, width=0.5) +
  ylab('Phone boundary error (ms)') + xlab('Number of adaptation speakers') +ggtitle('Phone boundary errors') +
  theme_memcauliffe() +facet_wrap(~language) + 
  geom_hline(aes(yintercept=mean*1000, color=adaptation), data=baseplotData,size=2) + scale_color_manual(values=c('#D43610','#8338EC','#6EC200', "#FB5607")) #+ 
  #geom_hline(aes(yintercept=mean*1000), data=subset(baseplotData, adaptation=='base'),color='#8338EC',size=2) + 
  #geom_hline(aes(yintercept=mean*1000), data=subset(baseplotData, adaptation=='manual'),color='#6EC200',size=2)

ggplot(aes(x=adaptation, y=mean * 1000), data=baseplotData) + geom_point(size = 5, color='#FB5607') +
  geom_errorbar(aes(ymin = (mean - ci) * 1000, ymax = (mean + ci)* 1000),size=2, width=0.5, color='#FB5607') +
  ylab('Phone boundary error (ms)') + xlab('Alignment condition') +ggtitle('Phone boundary errors') +
  theme_memcauliffe() +
  scale_x_discrete(guide = guide_axis(n.dodge = 2)) +facet_wrap(~language)

baseplotData$language <- factor(baseplotData$language, levels=c('arpa', 'english','german', 'czech', 'mandarin'))



ggplot(aes(x=adaptation, y=mean * 1000, color=language, group=language), data=baseplotData) + geom_point(size = 3) + geom_path(size=1) +
  #geom_errorbar(aes(ymin = (mean - ci) * 1000, ymax = (mean + ci)* 1000),size=2, width=0.5) +
  ylab('Phone boundary error (ms)') + xlab('Adaptation condition') +ggtitle('Phone boundary errors') +
  theme_memcauliffe_light() +
  scale_x_discrete(, labels=c("None", 'Naive', 'Reference'))+ scale_color_manual(values=cbbPalette, name="Language", labels=c('English ARPA', "English", 'German', "Czech", 'Mandarin'))



plotData <- summarySE(data=data, measurevar = 'phone_error_rate', groupvars=c('version', 'corpus','phone_set'))

ggplot(aes(x=version, y=mean * 100), data=plotData) + geom_point(size = 5, color='#FB5607') +
  geom_errorbar(aes(ymin = (mean - ci) * 100, ymax = (mean + ci)* 100),size=2, width=0.5, color='#FB5607') +
  ylab('Phone error rate %') + xlab('Alignment condition') +ggtitle('Phone error rate') +
  theme_memcauliffe() +
  scale_x_discrete(guide = guide_axis(n.dodge = 2)) + facet_trelliscope(phone_set~corpus, ncol = 2, scales="free_x")


labphon_data <- subset(data, corpus %in% c('timit', 'buckeye', 'csj', 'seoul') & evaluation %in% c('arpa_1.0', 'gp_1.0', 'mfa_3.0'))

labphon_data[labphon_data$evaluation == 'gp_1.0',]$evaluation = 'arpa_1.0'
labphon_data$evaluation <- factor(labphon_data$evaluation)


plotData <- summarySE(data=labphon_data, measurevar = 'alignment_score', groupvars=c('evaluation', 'corpus'))


ggplot(aes(x=evaluation, y=mean * 1000, color=corpus, group=corpus), data=plotData) +geom_path() + geom_point(size = 2.5)  +
  ylab('Phone boundary error (ms)') + xlab('MFA version') +ggtitle('Phone boundary errors') +
  theme_memcauliffe() +
  scale_x_discrete(labels=c("1.0", "3.0")) +
  scale_color_manual(values=cbbPalette, labels=c('Buckeye', 'CSJ', "Seoul", "TIMIT"), name='Corpus')

ggsave("docs/source/_static/benchmarks/phone_alignment.png", width=1000, height=800, units="px", dpi=200)


uw_colloquium_data <- subset(data, corpus %in% c('timit', 'buckeye', 'csj', 'seoul') & evaluation %in% c('mfa_3.0'))
uw_colloquium_data$corpus <- factor(uw_colloquium_data$corpu, levels=c('timit', 'buckeye', 'csj', 'seoul'))


plotData <- summarySE(data=uw_colloquium_data, measurevar = 'alignment_score', groupvars=c('corpus'))


ggplot(aes(x=corpus, y=mean * 1000), data=plotData) + geom_point(size = 6, color='#FB5607')  +
  ylab('Phone boundary error (ms)') + xlab('Corpus') +ggtitle('Phone boundary errors') +
  theme_memcauliffe() +
  scale_x_discrete(labels=c("English-TIMIT", 'English-Buckeye', 'Japanese-CSJ', "Korean-Seoul"))

ggsave("docs/source/_static/benchmarks/uw_phone_alignment.png", width=1500, height=800, units="px", dpi=150)



t <- subset(data, corpus=='seoul'& version=='3.0')


subset(data, corpus=='buckeye' & phone_set=='mfa') %>% group_by(version) %>% summarise(n())
