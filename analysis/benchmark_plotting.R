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

baseplotData$language <- factor(baseplotData$language, levels=c('arpa', 'english','german', 'czech', 'mandarin'))



ggplot(aes(x=adaptation, y=mean * 1000, color=language, group=language), data=baseplotData) + geom_point(size = 3) + geom_path(size=1) +
  #geom_errorbar(aes(ymin = (mean - ci) * 1000, ymax = (mean + ci)* 1000),size=2, width=0.5) +
  ylab('Phone boundary error (ms)') + xlab('Adaptation condition') +#ggtitle('Phone boundary errors') +
  theme_memcauliffe_light() +
  scale_x_discrete(, labels=c("None", 'Base', 'Reference'))+ scale_color_manual(values=cbbPalette, name="Language", labels=c('English ARPA', "English", 'German', "Czech", 'Mandarin'))

ggsave("case_study_three.png", width=1000, height=710, units="px", dpi=200)


ggplot(aes(x=adaptation, y=mean * 1000, color=language, group=language), data=subset(baseplotData, language %in% c('arpa', 'english'))) + geom_point(size = 3) + geom_path(size=1) +
  #geom_errorbar(aes(ymin = (mean - ci) * 1000, ymax = (mean + ci)* 1000),size=2, width=0.5) +
  ylab('Phone boundary error (ms)') + xlab('Adaptation condition') +#ggtitle('Phone boundary errors') +
  theme_memcauliffe_light() +
  scale_x_discrete(, labels=c("None", 'Base', 'Reference'))+ scale_color_manual(values=cbbPalette, name="Language", labels=c('English ARPA', "English", 'German', "Czech", 'Mandarin'))

ggsave("case_study_one.png", width=1000, height=710, units="px", dpi=200)


baseplotData <- summarySE(data=data, measurevar = 'phone_error_rate', groupvars=c('language', 'adaptation'))

baseplotData$language <- factor(baseplotData$language, levels=c('arpa', 'english','german', 'czech', 'mandarin'))

ggplot(aes(x=adaptation, y=mean * 100, color=language, group=language), data=baseplotData) + geom_point(size = 3) + geom_path(size=1) +
  #geom_errorbar(aes(ymin = (mean - ci) * 1000, ymax = (mean + ci)* 1000),size=2, width=0.5) +
  ylab('Phone error rate') + xlab('Adaptation condition') +#ggtitle('Phone boundary errors') +
  theme_memcauliffe_light() +
  scale_x_discrete(, labels=c("None", 'Base', 'Reference'))+ scale_color_manual(values=cbbPalette, name="Language", labels=c('English ARPA', "English", 'German', "Czech", 'Mandarin'))
