<%
    response.setHeader("Cache-Control", "no-cache");
    response.setDateHeader("Expires", System.currentTimeMillis());

    String sleep = request.getParameter("sleep");

    if (sleep != null) {
        try {
            Thread.sleep(Long.parseLong(sleep));
        } catch (InterruptedException e) {
        }
    }

    if (request.getParameter("error") != null) {
        response.sendError(HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "Very bad things happened!");
        return;
    }

    boolean json=request.getParameter("json")!=null;
    if(json){ %>
        {
            "servertime": "<%=System.currentTimeMillis() %>",
            "sleep": "<%=sleep %>"
        }
<%}else{%>
servertime: <%=System.currentTimeMillis()%> / sleep: <%=sleep%>
<%}%>
