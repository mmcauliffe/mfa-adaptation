library(tidyr)
library(dplyr)
library(readr)
library(stringr)
root_dir = "/Users/michael/Documents/Data/experiments/adaptation_benchmarking/varics_alignments"

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

data$evaluation = factor(data$evaluation)


data <- subset(data, !is.na(data$alignment_score))

plotData <- summarySE(data=data, measurevar = 'alignment_score', groupvars=c('evaluation'))

ggplot(aes(x=evaluation, y=mean * 1000), data=plotData) + geom_point(size = 5, color='#053561') +
  #geom_errorbar(aes(ymin = (mean - ci) * 1000, ymax = (mean + ci)* 1000),size=2, width=0.5, color='#FB5607') +
  ylab('Phone boundary error (ms)') + xlab('Adaptation condition') +#ggtitle('Phone boundary errors') +
  theme_memcauliffe_light() +
  scale_x_discrete(labels=c('None', 'Base', 'Corrected', "Corrected+"))
ggsave("static/case_study_two.png", width=1000, height=710, units="px", dpi=200)

plotData <- summarySE(data=data, measurevar = 'phone_error_rate', groupvars=c('version', 'corpus','phone_set'))

ggplot(aes(x=version, y=mean * 100), data=plotData) + geom_point(size = 5, color='#FB5607') +
  geom_errorbar(aes(ymin = (mean - ci) * 100, ymax = (mean + ci)* 100),size=2, width=0.5, color='#FB5607') +
  ylab('Phone error rate %') + xlab('Alignment condition') +ggtitle('Phone error rate') +
  theme_memcauliffe() +
  scale_x_discrete(guide = guide_axis(n.dodge = 2)) + facet_trelliscope(phone_set~corpus, ncol = 2, scales="free_x")

