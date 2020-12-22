from bs4 import BeautifulSoup
import requests
import time
from urllib.parse import unquote

current_milli_time = lambda: int(round(time.time()*1000))
philosophyURL = "https://fr.wikipedia.org/wiki/Philosophie"
nodes = {}

def getTitle(link):
  n = unquote(link[30:])
  return n.replace("_", " ")

def isValid(ref,paragraph):
  # Check whether the reference is valid in the paragraph
  if not ref or "#" in ref or "//" in ref or ":" in ref:
    return False
  if "/wiki/" not in ref:
    return False
  if ref not in paragraph:
    return False
  prefix = paragraph.split(ref,1)[0]
  if prefix.count("(")!=prefix.count(")") or prefix.count("/")!=prefix.count("/"):
    return False
  return True

def initFiles(fileNodes, FileEdges):
    fileNodes.write("id,Label\n")
    fileEdges.write("id,Source,Target\n")

def processLink(link, visited, fileNodes, fileEdges, iteration, startTime, firstTitle, lastUsedNodeID, lastNodeID, lastEdgeID, newArticle, base="https://fr.wikipedia.org"):
    r = requests.get(link)
    soup = BeautifulSoup(r.text, "html.parser")
    body = soup.find(class_="mw-parser-output")

    title = getTitle(r.url)
    if firstTitle == "":
        firstTitle = title
        print("===== " + title.upper() + " =====")
    else:
      print("   " + u"\u2514 " + title)

    if r.url not in nodes:
      currentNodeID = lastNodeID + 1
      nodes[link] = currentNodeID
      nodeID = currentNodeID
      fileNodes.write(str(currentNodeID) + "," + title + "\n")
    else:
      currentNodeID = lastNodeID
      nodeID = nodes[link]
    
    if not newArticle:
      currentEdgeID = lastEdgeID+1
      fileEdges.write(str(currentEdgeID) + "," + str(lastUsedNodeID) + "," + str(nodeID) + "\n")
    else:
      currentEdgeID = lastEdgeID

    if link not in visited:
        visited.append(link)
        nextLink = None
        for paragraph in body.find_all(["p", "ul"], recursive=False):
          for link in paragraph.find_all("a"):
            ref = link.get("href")
            if link.get("class") != None:
              continue
            if isValid(str(ref),str(paragraph)):
              nextLink = base + ref
              break
          if nextLink:
            break

        if not nextLink:
          print("No NEXTLINK")
          return (lastNodeID+1,lastEdgeID+1)

        iteration += 1
        lastNodeID, lastEdgeID = processLink(nextLink, visited, fileNodes, fileEdges, iteration, startTime, firstTitle, nodeID, currentNodeID, currentEdgeID, False)
        return (lastNodeID,lastEdgeID)
    else:
      print(str(firstTitle) + " : " + str(iteration) + " itérations avant de boucler, en " + str((current_milli_time() - startTime)/1000) + " secondes. Arret sur " + link)
      return (lastNodeID+1,lastEdgeID+1)


        


nbr = int(input("How much wiki articles to crawl ? "))

fileNodes = open("nodes.csv", "a+", encoding="utf8")
fileEdges = open("edges.csv", "a+", encoding="utf8")

initFiles(fileNodes, fileEdges)
lastNodeID, lastEdgeID = (0,0)

for i in range(nbr):
    print("Nbr : " + str(i))
    lastNodeID, lastEdgeID = processLink("https://fr.wikipedia.org/wiki/Sp%C3%A9cial:Page_au_hasard", [philosophyURL], fileNodes, fileEdges, 0, current_milli_time(), "", 0, lastNodeID, lastEdgeID, True)
