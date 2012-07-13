# -*- coding: utf-8 -*-
"""\
This is a python port of "Goose" orignialy licensed to Gravity.com
under one or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership. 

Python port was written by Xavier Grangier for Recrutae

Gravity.com licenses this file
to you under the Apache License, Version 2.0 (the "License"); 
you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import os
from copy import deepcopy
from goose.Article import Article
from goose.utils import URLHelper
from goose.extractors import StandardContentExtractor
from goose.cleaners import StandardDocumentCleaner
from goose.outputformatters import StandardOutputFormatter
from goose.parsers import Parser
from goose.images.UpgradedImageExtractor import UpgradedImageIExtractor
from network import get_html

class CrawlCandidate(object):
    
    def __init__(self, config, url, rawHTML):
        self.config = config
        self.url = url
        self.rawHTML = rawHTML
    


class Crawler(object):
    
    def __init__(self, config):
        self.config = config
        self.logPrefix = "crawler:"
        
    def crawl(self, crawlCandidate):
        options = crawlCandidate.options
        article = Article()
        
        parseCandidate = URLHelper.getCleanedUrl(crawlCandidate.url)
        rawHtml = self.getHTML(crawlCandidate, parseCandidate)
        
        if rawHtml is None:
            return article
        
        doc = self.getDocument(parseCandidate.url, rawHtml)
        
        
        extractor = self.getExtractor()
        docCleaner = self.getDocCleaner()
        outputFormatter = self.getOutputFormatter()
        
        # article
        article.finalUrl = parseCandidate.url
        article.linkhash = parseCandidate.linkhash
        article.rawHtml = rawHtml
        article.title = extractor.getTitle(article)
        article.metaLang = extractor.getMetaLang(article)
        article.metaFavicon = extractor.getMetaFavicon(article)
        article.metaDescription = extractor.getMetaDescription(article)
        article.metaKeywords = extractor.getMetaKeywords(article)
        article.canonicalLink = extractor.getCanonicalLink(article)
        article.domain = extractor.getDomain(article.finalUrl)
        article.tags = extractor.extractTags(article)

        # if the user requested a full body response
        if options.enableBodyAnalysis:
            article.doc = doc
            article.rawDoc = deepcopy(doc)
            article.doc = docCleaner.clean(article)

            # big stuff
            article.topNode = extractor.calculateBestNodeBasedOnClustering(article)
            if article.topNode is not None:
                if self.config.enableImageFetching:
                    imageExtractor = self.getImageExtractor(article)
                    article.topImage = imageExtractor.getBestImage(article.rawDoc, article.topNode)

                article.topNode = extractor.postExtractionCleanup(article.topNode)
                article.cleanedArticleText = outputFormatter.getFormattedText(article.topNode)

        return article
        
    def getHTML(self, crawlCandidate, parsingCandidate):
        if crawlCandidate.rawHTML:
            return crawlCandidate.rawHTML
        else:
            # fetch HTML
            html = get_html(parsingCandidate.url, self.config)
            return html
    
    
    def getImageExtractor(self, article):
        httpClient = None
        return UpgradedImageIExtractor(httpClient, article, self.config)
    
    
    def getOutputFormatter(self):
        return StandardOutputFormatter()
    
    
    def getDocCleaner(self):
        return StandardDocumentCleaner()
    
    
    def getDocument(self, url, rawHtml):
        doc = Parser.fromstring(rawHtml)
        return doc
    
    
    def getExtractor(self):
        return StandardContentExtractor()
    
    
    def releaseResources(self, article):
        directory = self.config.localStoragePath
        for fname in os.listdir(directory):
            f = '%s/%s' % (self.config.localStoragePath, fname)
            try:
                os.remove(f)
            except OSError:
                # TODO better log handeling
                pass
                
                
        
            
